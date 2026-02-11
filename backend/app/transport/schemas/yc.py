from datetime import datetime

from sqlmodel import SQLModel


class YCFounderPublic(SQLModel):
    name: str
    twitter_url: str | None = None
    linkedin_url: str | None = None


class YCCompanyPublic(SQLModel):
    yc_id: int
    name: str
    slug: str
    batch: str
    batch_code: str
    year: int
    status: str
    industry: str | None
    website: str | None
    all_locations: str | None
    one_liner: str | None
    team_size: int | None
    small_logo_thumb_url: str | None
    url: str
    is_hiring: bool
    nonprofit: bool
    top_company: bool
    tags: list[str]
    industries: list[str] = []
    regions: list[str] = []
    founders: list[YCFounderPublic] = []


class YCCompaniesPublic(SQLModel):
    data: list[YCCompanyPublic]
    count: int


class YCSearchMeta(SQLModel):
    statuses: list[str]
    years: list[int]
    batches: list[str]
    industries: list[str]


class YCSyncStatePublic(SQLModel):
    last_started_at: datetime | None
    last_finished_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    last_item_count: int | None

