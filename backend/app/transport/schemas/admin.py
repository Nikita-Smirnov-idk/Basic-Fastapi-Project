from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["admin"], prefix="/admin")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False
    plan: str = "free"
    balance_cents: int = 0

class AdminDashboardStats(BaseModel):
    total_users: int
    paying_users: int
    total_balance_cents: int
    yc_companies_count: int
    yc_founders_count: int

class BalanceUpdate(BaseModel):
    amount_cents: int = Field(..., gt=0, description="Positive amount to add in cents")