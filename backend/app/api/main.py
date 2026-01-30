from fastapi import APIRouter

from app.api.routes.utils import utils
from app.api.routes.admin import admin
from app.api.routes.users import users
from app.api.routes.items import items
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(admin.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)