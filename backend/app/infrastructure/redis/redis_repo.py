import json
import logging
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError, RedisError, TimeoutError

from app.core.config.config import settings

logger = logging.getLogger(__name__)


class RedisRepository:
    FAMILY_PREFIX = "family:"
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

    async def store_refresh_token(
        self,
        user_id: str,
        user_agent: str,
        jti: str,
        family_id: str,
    ) -> str:
        try:
            family_data: dict

            family_old_data = await self.redis_client.get(
                self.FAMILY_PREFIX + family_id
            )
            if not family_old_data:
                family_data = {
                    "sub": user_id,
                    "current_jti": jti,
                    "user_agent": user_agent,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "blocked": False,
                }
            else:
                parsed = json.loads(family_old_data)
                family_data = {
                    "sub": parsed["sub"],
                    "current_jti": jti,
                    "user_agent": parsed["user_agent"],
                    "created_at": parsed["created_at"],
                    "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "blocked": parsed.get("blocked", False),
                }

            pipe = self.redis_client.pipeline(transaction=True)
            pipe.set(
                self.FAMILY_PREFIX + family_id,
                json.dumps(family_data),
                ex=self.EXPIRE_TIME,
            )
            user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
            pipe.sadd(user_sessions_key, family_id)
            pipe.expire(user_sessions_key, self.EXPIRE_TIME)
            await pipe.execute()
            return family_id
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning("Redis error: %s", type(e).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable. Please try again later.",
            ) from e

    async def get_family_data(self, family_id: str) -> dict | None:
        try:
            raw_data = await self.redis_client.get(self.FAMILY_PREFIX + family_id)
            if raw_data:
                return json.loads(raw_data)
            return None
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
