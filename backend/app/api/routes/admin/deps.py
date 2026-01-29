import logging
from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.models.db.models import User
from app.api.deps import CurrentUser

logger = logging.getLogger(__name__)


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        logger.warning("Insufficient privileges, user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user

AdminDep = Annotated[User, Depends(get_current_active_superuser)]

