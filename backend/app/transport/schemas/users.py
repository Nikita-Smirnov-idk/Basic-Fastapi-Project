"""Request/response schemas for users/auth. Transport layer only."""
import uuid
from typing import List

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel


class UserBaseSchema(SQLModel):
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    plan: str = Field(default="free", max_length=32)
    balance_cents: int = 0


class UserCreate(UserBaseSchema):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBaseSchema):
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBaseSchema):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class SessionOut(BaseModel):
    family_id: str
    user_agent: str
    created_at: str
    last_active: str

    class Config:
        from_attributes = True


class SessionsListOut(SQLModel):
    sessions: List[SessionOut]
    total: int


class BlockSessionRequest(BaseModel):
    family_id: str


class StartSignupRequest(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class CompleteSignupRequest(SQLModel):
    token: str
