import logging
from typing import Annotated

from app.db.postgres.unit_of_work import UnitOfWork
from app.db.redis.redis_repo import RedisRepository
from app.services.users.google_auth.google_auth import GoogleAuthService

from fastapi import Depends

logger = logging.getLogger(__name__)


def get_google_auth_service(uow: UnitOfWork = Depends(), redis: RedisRepository = Depends()) -> GoogleAuthService:
    return GoogleAuthService(uow=uow, redis_repo=redis)

GoogleAuthServiceDep = Annotated[GoogleAuthService, Depends(get_google_auth_service)]