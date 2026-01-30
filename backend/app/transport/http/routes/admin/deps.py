from typing import Annotated

from fastapi import Depends

from app.infrastructure.persistence.models import User
from app.transport.http.deps import CurrentUser, get_current_active_superuser

AdminDep = Annotated[User, Depends(get_current_active_superuser)]
