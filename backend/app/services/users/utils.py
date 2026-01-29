from typing import Dict

from fastapi import HTTPException, status
from app.models.db.models import User
from app.services.jwt import tokens
from app.db.redis.redis_repo import RedisRepository


async def create_and_store_tokens(
        redis: RedisRepository,
        user_id: str,
        user_agent: str,
    ) -> Dict[str, str]:
        access_token = tokens.create_access_token({"sub": str(user_id)})
        refresh_token = tokens.create_refresh_token({"sub": str(user_id)})

        await redis.store_refresh_token(
            user_id=str(user_id),
            refresh_token=refresh_token,
            user_agent=user_agent,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user_id,
        }