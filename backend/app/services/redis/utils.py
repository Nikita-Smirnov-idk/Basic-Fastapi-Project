from .database import redis_client, SessionLocal
from .models import User
from .utils import create_access_token, create_refresh_token, decode_token
import uuid
import json
from redis import asyncio as aioredis
from fastapi import Depends
from app.core.config import settings

REFRESH_PREFIX = "refresh:"
BLOCKLIST_PREFIX = "blocklist:"
FAMILY_BLOCK_PREFIX = "family_block:"

def store_refresh_token(user_id: int, refresh_token: str, user_agent: str, redis_client: aioredis.Redis, family_id: str = None):
    if not family_id:
        family_id = str(uuid.uuid4())  # Новый family_id при первом логине
    data = {
        "user_id": user_id,
        "user_agent": user_agent,
        "family_id": family_id
    }
    redis_client.set(REFRESH_PREFIX + refresh_token, json.dumps(data), ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)  # TTL в секундах
    return family_id

def get_refresh_data(redis_client: aioredis.Redis, refresh_token: str):
    data = redis_client.get(REFRESH_PREFIX + refresh_token)
    if data:
        return json.loads(data)
    return None

def add_to_blocklist(redis_client: aioredis.Redis, token: str):
    redis_client.set(BLOCKLIST_PREFIX + token, "blocked", ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

def is_in_blocklist(redis_client: aioredis.Redis, token: str):
    return redis_client.exists(BLOCKLIST_PREFIX + token)

def block_family(redis_client: aioredis.Redis, family_id: str):
    redis_client.set(FAMILY_BLOCK_PREFIX + family_id, "blocked", ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

def is_family_blocked(redis_client: aioredis.Redis, family_id: str):
    return redis_client.exists(FAMILY_BLOCK_PREFIX + family_id)