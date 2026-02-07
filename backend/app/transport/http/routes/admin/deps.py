from typing import Annotated

from fastapi import Depends

from app.domain.entities.db.user import User
from app.transport.http.deps import CurrentUser, get_current_active_superuser

AdminDep = Annotated[User, Depends(get_current_active_superuser)]
