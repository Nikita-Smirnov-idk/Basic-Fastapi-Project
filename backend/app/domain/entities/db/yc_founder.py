import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class YCFounder(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    company_id: uuid.UUID = Field(
        foreign_key="yccompany.id",
        nullable=False,
        index=True,
        ondelete="CASCADE",
    )
    sort_order: int = Field(default=0, index=True)

    name: str = Field(max_length=255, index=True)
    role: str | None = Field(default=None, max_length=64)
    bio: str | None = Field(default=None)

    yc_profile_url: str | None = Field(default=None, max_length=2048)
    twitter_url: str | None = Field(default=None, max_length=2048)
    linkedin_url: str | None = Field(default=None, max_length=2048)

    avatar_url: str | None = Field(default=None, max_length=2048)

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

