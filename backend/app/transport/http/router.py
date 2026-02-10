"""HTTP API router: all routes under API_V1_STR. Composed in app."""
from fastapi import APIRouter

from app.transport.http.routes import admin, items, users, utils
from app.transport.http.routes import yc_directory

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(admin.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(yc_directory.router)
