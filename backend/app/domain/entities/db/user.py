"""
DB models (SQLModel table=True). Used only by persistence layer and Alembic.
Domain entities live in domain/entities; transport schemas in transport/schemas.
"""
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from .item import Item


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    plan: str = Field(default="free", max_length=32, index=True)
    balance_cents: int = Field(default=0, index=True)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = Field(default=None)
    google_id: str | None = Field(default=None, unique=True, index=True, max_length=255)
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
