from redis import asyncio as aioredis
from app.core.config import settings

# Initialize the Redis client
redis_client: aioredis.Redis = aioredis.from_url(
    settings.REDIS_URI,
    decode_responses=True,  # Automatically decode responses to strings
    max_connections=50,
    retry_on_timeout=True,
)

def get_redis_client() -> aioredis.Redis:
    """ Dependency to inject Redis client into routes/services """
    return redis_client