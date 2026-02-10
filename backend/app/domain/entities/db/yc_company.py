import uuid
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class YCCompany(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    yc_id: int = Field(index=True, unique=True)
    name: str = Field(max_length=255, index=True)
    slug: str = Field(max_length=255, index=True)

    batch: str = Field(max_length=64, index=True)
    batch_code: str = Field(max_length=8, index=True)
    year: int = Field(index=True)

    status: str = Field(max_length=32, index=True)
    industry: str | None = Field(default=None, max_length=128, index=True)
    subindustry: str | None = Field(default=None, max_length=255)

    website: str | None = Field(default=None, max_length=2048)
    all_locations: str | None = Field(default=None, max_length=512)

    one_liner: str | None = Field(default=None, max_length=512)
    long_description: str | None = Field(default=None)
    team_size: int | None = Field(default=None, index=True)

    small_logo_thumb_url: str | None = Field(default=None, max_length=2048)
    url: str = Field(max_length=2048)

    is_hiring: bool = Field(default=False, index=True)
    nonprofit: bool = Field(default=False, index=True)
    top_company: bool = Field(default=False, index=True)

    industries: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    regions: list[str] = Field(default_factory=list, sa_column=Column(JSONB))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSONB))

    launched_at: int | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)

