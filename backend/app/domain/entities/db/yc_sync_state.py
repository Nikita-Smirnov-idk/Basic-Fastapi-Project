import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class YCSyncState(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    source: str = Field(default="yc_directory", max_length=64, unique=True, index=True)
    last_started_at: datetime | None = Field(default=None)
    last_finished_at: datetime | None = Field(default=None)
    last_success_at: datetime | None = Field(default=None)
    last_error: str | None = Field(default=None, max_length=2048)
    last_item_count: int | None = Field(default=None)

