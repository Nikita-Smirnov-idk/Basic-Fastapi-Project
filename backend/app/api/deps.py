from collections.abc import Generator
from typing import Annotated

from redis import asyncio as aioredis
import jwt
from fastapi import Cookie, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.models.db.models import User
from app.models.users.models import TokenPayload
from app.services.jwt.tokens import decode_token
from app.core.redis import get_redis_client

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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type: access token required",
            )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

def get_user_agent(user_agent: str = Header(None)):
    return user_agent


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_refresh_token_from_cookie(
    refresh_token: str | None = Cookie(default=None, alias="refresh_token")
) -> str | None:
    return refresh_token

CurrentRefreshToken = Annotated[str, Depends(get_refresh_token_from_cookie)]
AdminDep = Annotated[User, Depends(get_current_active_superuser)]