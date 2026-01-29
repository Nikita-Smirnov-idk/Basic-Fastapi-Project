import logging
from typing import Annotated

from app.db.postgres.unit_of_work import UnitOfWork
from app.db.redis.redis_repo import RedisRepository
from app.services.users.auth.auth_service import AuthService
from fastapi import Cookie, Depends

logger = logging.getLogger(__name__)

def get_refresh_token_from_cookie(
    refresh_token: str | None = Cookie(default=None, alias="refresh_token")
) -> str | None:
    return refresh_token


def get_auth_service(uow: UnitOfWork = Depends(), redis: RedisRepository = Depends()) -> AuthService:
    return AuthService(uow=uow, redis_repo=redis)

RefreshTokenDep = Annotated[str | None, Depends(get_refresh_token_from_cookie)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]