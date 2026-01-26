from fastapi import APIRouter

from app.api.routes.utils import utils
from app.api.routes.admin import admin
from app.api.routes.users import users
from app.api.routes.items import items
from app.api.routes.auth import auth
from app.api.routes.passwords import passwords
from app.api.routes.google import google
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(passwords.router)
api_router.include_router(users.router)

api_router.include_router(admin.router)

api_router.include_router(utils.router)
api_router.include_router(items.router)

if settings.GOOGLE_CLIENT_ID is not None and settings.GOOGLE_CLIENT_SECRET is not None:
    api_router.include_router(google.router)