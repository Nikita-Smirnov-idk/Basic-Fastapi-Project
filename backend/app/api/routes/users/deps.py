import logging
from typing import Annotated

from app.db.postgres.unit_of_work import UnitOfWork
from app.db.redis.redis_repo import RedisRepository
from app.services.users.user_service import UserService
from fastapi import Depends

logger = logging.getLogger(__name__)
def get_user_service(uow: UnitOfWork = Depends(), redis: RedisRepository = Depends()) -> UserService:
    return UserService(uow=uow, redis_repo=redis)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]