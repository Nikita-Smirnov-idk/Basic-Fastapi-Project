"""Domain entity: User. No DB/ORM dependencies."""
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """User domain entity. Used by use cases and domain logic."""

    id: UUID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    full_name: str | None = None
    hashed_password: str | None = None
    google_id: str | None = None

    model_config = {"from_attributes": True}
