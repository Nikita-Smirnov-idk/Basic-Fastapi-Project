import json
import logging
import hashlib
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.config import settings

logger = logging.getLogger(__name__)


class RedisRepository:
    REFRESH_PREFIX = "refresh:"
    FAMILY_PREFIX = "family:"
    REFRESH_BLOCKLIST_PREFIX = "refresh_block:"
    USER_SESSIONS_PREFIX = "user_sessions:"

    TOKEN_PEPPER = settings.TOKEN_PEPPER
    EXPIRE_TIME = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

    def __init__(self) -> None:
        self.redis_client: aioredis.Redis = aioredis.from_url(
            settings.REDIS_URI,
            decode_responses=True,
            max_connections=50,
            retry_on_timeout=True,
        )

    @classmethod
    def hash_refresh_token(cls, token: str) -> str:
        input_bytes = (token + cls.TOKEN_PEPPER).encode("utf-8")
        return hashlib.sha256(input_bytes).hexdigest()

    async def store_refresh_token(
        self,
        user_id: str,
        refresh_token: str,
        user_agent: str,
        family_id: str | None = None,
    ) -> str:
        try:
            family_data: dict
            if not family_id:
                family_id = str(uuid.uuid4())
                family_data = {
                    "user_agent": user_agent,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "blocked": False,
                }
            else:
                family_old_data = await self.redis_client.get(
                    self.FAMILY_PREFIX + family_id
                )
                if family_old_data is None:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid token",
                    )
                family_old_data = json.loads(family_old_data)
                family_data = {
                    "user_agent": family_old_data["user_agent"],
                    "created_at": family_old_data["created_at"],
                    "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "blocked": family_old_data.get("blocked", False),
                }

            pipe = self.redis_client.pipeline(transaction=True)
            token_hash = self.hash_refresh_token(refresh_token)
            pipe.set(
                self.FAMILY_PREFIX + family_id,
                json.dumps(family_data),
                ex=self.EXPIRE_TIME,
            )
            user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
            pipe.sadd(user_sessions_key, family_id)
            pipe.expire(user_sessions_key, self.EXPIRE_TIME)
            data = {
                "user_id": user_id,
                "user_agent": user_agent,
                "family_id": family_id,
            }
            pipe.set(
                self.REFRESH_PREFIX + token_hash,
                json.dumps(data),
                ex=self.EXPIRE_TIME,
            )
            await pipe.execute()
            return family_id
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    async def get_refresh_data(self, refresh_token: str) -> dict | None:
        try:
            token_hash = self.hash_refresh_token(refresh_token)
            raw_data = await self.redis_client.get(self.REFRESH_PREFIX + token_hash)
            if raw_data:
                return json.loads(raw_data)
            return None
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    async def block_refresh(self, token: str) -> None:
        try:
            token_hash = self.hash_refresh_token(token)
            await self.redis_client.set(
                self.REFRESH_BLOCKLIST_PREFIX + token_hash,
                "blocked",
                ex=self.EXPIRE_TIME,
            )
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    async def is_refresh_blocked(self, token: str) -> bool:
        try:
            token_hash = self.hash_refresh_token(token)
            exists = await self.redis_client.exists(
                self.REFRESH_BLOCKLIST_PREFIX + token_hash
            )
            return exists > 0
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    async def block_family(self, family_id: str, user_id: str) -> None:
        try:
            pipe = self.redis_client.pipeline(transaction=True)
            user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
            pipe.srem(user_sessions_key, family_id)
            key = self.FAMILY_PREFIX + family_id
            raw = await self.redis_client.get(key)
            if not raw:
                await pipe.execute()
                return
            data = json.loads(raw)
            data["blocked"] = True
            pipe.set(key, json.dumps(data), ex=self.EXPIRE_TIME)
            await pipe.execute()
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    async def is_family_blocked(self, family_id: str) -> bool:
        try:
            raw = await self.redis_client.get(self.FAMILY_PREFIX + family_id)
            if not raw:
                return False
            data = json.loads(raw)
            return data.get("blocked", False) is True
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    async def get_sessions_by_user_id(self, user_id: str) -> dict:
        try:
            user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
            family_ids = await self.redis_client.smembers(user_sessions_key)
            if not family_ids:
                return {}
            pipe = self.redis_client.pipeline(transaction=True)
            for fid in family_ids:
                pipe.get(self.FAMILY_PREFIX + fid)
            raw_values = await pipe.execute()
            sessions_data: dict = {}
            for fid, raw in zip(family_ids, raw_values, strict=True):
                if raw:
                    sessions_data[fid] = json.loads(raw)
            return sessions_data
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    def get_client(self) -> aioredis.Redis:
        return self.redis_client


redis_repo = RedisRepository()


def get_redis_repo() -> RedisRepository:
    return redis_repo
