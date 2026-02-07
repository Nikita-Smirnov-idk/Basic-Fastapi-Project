# item.py
import uuid
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

if TYPE_CHECKING:
    from .user import User  # Only for type hints, won't import at runtime

class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: Optional["User"] = Relationship(back_populates="items")  # string literal!
