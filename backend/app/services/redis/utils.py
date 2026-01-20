import uuid
import json
import hashlib
from redis import asyncio as aioredis
from app.core.config import settings
from datetime import datetime

# Константы
REFRESH_PREFIX = "refresh:"
FAMILY_PREFIX = "family:"
REFRESH_BLOCKLIST_PREFIX = "refresh_block:"
USER_SESSIONS_PREFIX = "user_sessions:"

TOKEN_PEPPER = settings.TOKEN_PEPPER

EXPIRE_TIME = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400


def hash_refresh_token(token: str) -> str:
    """
    Вычисляет SHA-256 хэш от (token + pepper)
    Возвращает hex-строку (64 символа)
    """
    input_bytes = (token + TOKEN_PEPPER).encode("utf-8")
    return hashlib.sha256(input_bytes).hexdigest()


async def store_refresh_token(
    user_id: uuid.UUID | str,
    refresh_token: str,
    user_agent: str,
    redis_client: aioredis.Redis,
    family_id: str = None
) -> str:
    """
    Сохраняет refresh-токен в Redis по его хэшу.
    Возвращает family_id.
    """
    family_data = dict()
    if not family_id:
        family_id = str(uuid.uuid4())
        family_data = {
            "user_agent": user_agent,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "blocked": False,
        }
    else:
        family_old_data = await redis_client.get(FAMILY_PREFIX + family_id)
        if family_old_data is None:
            return None
        
        family_old_data = json.loads(family_old_data)
        family_data = {
            "user_agent": family_old_data["user_agent"],
            "created_at": family_old_data["created_at"],
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "blocked": family_old_data.get("blocked", False),
        }

    pipe = redis_client.pipeline()

    token_hash = hash_refresh_token(refresh_token)

    pipe.set(
        FAMILY_PREFIX + family_id,
        json.dumps(family_data),
        ex=EXPIRE_TIME
    )

    # Добавляем family_id в set пользователя (если ещё нет)
    user_sessions_key = USER_SESSIONS_PREFIX + str(user_id)
    pipe.sadd(user_sessions_key, family_id)
    pipe.expire(user_sessions_key, EXPIRE_TIME)

    data = {
        "user_id": str(user_id),
        "user_agent": user_agent,
        "family_id": family_id,
    }

    pipe.set(
        REFRESH_PREFIX + token_hash,
        json.dumps(data),
        ex=EXPIRE_TIME
    )

    await pipe.execute()

    return family_id


async def get_refresh_data(redis_client: aioredis.Redis, refresh_token: str):
    """
    Получает метаданные по хэшу переданного refresh-токена.
    """
    token_hash = hash_refresh_token(refresh_token)
    raw_data = await redis_client.get(REFRESH_PREFIX + token_hash)
    if raw_data:
        return json.loads(raw_data)
    return None


async def block_refresh(redis_client: aioredis.Redis, token: str):
    """
    Добавляет токен в блок-лист (по хэшу).
    """
    token_hash = hash_refresh_token(token)
    await redis_client.set(
        REFRESH_BLOCKLIST_PREFIX + token_hash,
        "blocked",
        ex=EXPIRE_TIME
    )


async def is_refresh_blocked(redis_client: aioredis.Redis, token: str) -> bool:
    """
    Проверяет, находится ли токен в блок-листе.
    """
    token_hash = hash_refresh_token(token)
    exists = await redis_client.exists(REFRESH_BLOCKLIST_PREFIX + token_hash)
    return exists > 0


async def block_family(redis_client: aioredis.Redis, family_id: str, user_id: uuid.UUID | str):
    """
    Блокирует всю семью токенов (по family_id — без хэша).
    """
    pipe = redis_client.pipeline()
    user_sessions_key = USER_SESSIONS_PREFIX + str(user_id)
    pipe.srem(user_sessions_key, family_id)

    key = FAMILY_PREFIX + family_id
    raw = await redis_client.get(key)
    if not raw:
        await pipe.execute()
        return

    data = json.loads(raw)
    data["blocked"] = True

    pipe.set(key, json.dumps(data), ex=EXPIRE_TIME)

    await pipe.execute()



async def is_family_blocked(redis_client: aioredis.Redis, family_id: str) -> bool:
    """Проверяет флаг blocked внутри данных семьи"""
    raw = await redis_client.get(FAMILY_PREFIX + family_id)
    if not raw:
        return False

    data = json.loads(raw)
    return data.get("blocked", False) is True   


async def get_sessions_by_user_id(redis_client: aioredis.Redis, user_id: uuid.UUID | str) -> dict:
    """
    Получить список сессий юзера по его id
    """
    user_sessions_key = USER_SESSIONS_PREFIX + str(user_id)
    family_ids = await redis_client.smembers(user_sessions_key)

    if not family_ids:
        return {}

    pipe = redis_client.pipeline()
    for fid in family_ids:
        pipe.get(FAMILY_PREFIX + fid)

    raw_values = await pipe.execute()

    sessions_data = {}
    for fid, raw in zip(family_ids, raw_values):
        if raw:
            sessions_data[fid] = json.loads(raw)

    return sessions_data