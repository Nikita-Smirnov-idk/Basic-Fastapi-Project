import logging
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from redis import asyncio as aioredis
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.models.db.models import User
from app.models.users.models import TokenPayload
from app.services.jwt.tokens import decode_token
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
RedisDep = Annotated[aioredis.Redis, Depends(get_redis_client)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            logger.warning("Invalid token type")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type: access token required",
            )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError, ValueError):
        logger.warning("Invalid credentials")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        logger.warning("User not found, user_id=%s", token_data.sub)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        logger.warning("Inactive user, user_id=%s", user.id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

def get_user_agent(user_agent: str = Header(None)):
    if user_agent is None:
        user_agent = "Unknown user agent"
    return user_agent


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        logger.warning("Insufficient privileges, user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_refresh_token_from_cookie(
    refresh_token: str | None = Cookie(default=None, alias="refresh_token")
) -> str | None:
    return refresh_token

CurrentRefreshToken = Annotated[str | None, Depends(get_refresh_token_from_cookie)]
AdminDep = Annotated[User, Depends(get_current_active_superuser)]