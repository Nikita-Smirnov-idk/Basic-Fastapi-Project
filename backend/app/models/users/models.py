import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from app.models.db.models import UserBase
from pydantic import BaseModel
from typing import List

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)



# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# JSON payload containing access token
class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
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
        from_attributes = True  # для совместимости с dict


class SessionsListOut(BaseModel):
    sessions: List[SessionOut]
    total: int


class BlockSessionRequest(BaseModel):
    family_id: str


class StartSignupRequest(SQLModel):
    email: EmailStr = Field(max_length=255)


class CompleteSignupRequest(SQLModel):
    token: str
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)