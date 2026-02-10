"""HTTP API router: all routes under API_V1_STR. Composed in app."""
from app.transport.http.routes.utils import utils
from fastapi import APIRouter

from app.transport.http.routes import admin, users, utils
from app.transport.http.routes.yc import yc_directory

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(admin.router)
api_router.include_router(utils.router)
api_router.include_router(yc_directory.router)
