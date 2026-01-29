import logging
from typing import Annotated

from app.db.postgres.unit_of_work import UnitOfWork
from app.db.redis.redis_repo import RedisRepository
from app.services.users.passwords.passwords_service import PasswordService
from fastapi import Depends

logger = logging.getLogger(__name__)
def get_password_service(uow: UnitOfWork = Depends(), redis: RedisRepository = Depends()) -> PasswordService:
    return PasswordService(uow=uow, redis_repo=redis)

PasswordServiceDep = Annotated[PasswordService, Depends(get_password_service)]