"""Domain entity: Item. No DB/ORM dependencies."""
from uuid import UUID

from pydantic import BaseModel


class Item(BaseModel):
    """Item domain entity. Used by use cases and domain logic."""

    id: UUID
    title: str
    description: str | None = None
    owner_id: UUID

    model_config = {"from_attributes": True}
