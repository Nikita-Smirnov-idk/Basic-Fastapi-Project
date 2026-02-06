"""App Redis client. Used by infrastructure and app scripts."""
from redis import asyncio as aioredis
from app.core.config.config import settings

redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URI,
    decode_responses=True,
    max_connections=50,
    retry_on_timeout=True,
)


def get_redis_client() -> aioredis.Redis:
    return redis_client
