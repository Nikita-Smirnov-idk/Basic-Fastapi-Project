"""Request/response schemas for items. Transport layer only."""
import uuid

from sqlmodel import Field, SQLModel


class ItemBaseSchema(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBaseSchema):
    pass


class ItemUpdate(ItemBaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class ItemPublic(ItemBaseSchema):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int
