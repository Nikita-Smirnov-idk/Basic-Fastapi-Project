import logging
from collections.abc import Generator
from typing import Annotated

from app.db.postgres.unit_of_work import UnitOfWork
from app.db.redis.redis_repo import RedisRepository
from app.services.users.auth.auth_service import AuthService
from app.services.users.google_auth.google_auth import GoogleAuthService
from app.services.users.passwords.passwords_service import PasswordService
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
from app.db.postgres.session import get_async_session

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/"
)


SessionDep = Annotated[Session, Depends(get_async_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            logger.warning("Invalid token type")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type: access token required",
            )
        if payload.get("iss") != settings.FRONTEND_HOST:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token payload"
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user

def get_user_agent(user_agent: str = Header(None)):
    if user_agent is None:
        user_agent = "Unknown user agent"
    return user_agent


CurrentUser = Annotated[User, Depends(get_current_user)]
UserAgentDep = Annotated[str, Depends(get_user_agent)]