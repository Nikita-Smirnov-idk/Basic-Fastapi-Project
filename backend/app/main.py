import logging
import time

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config.config import settings
from app.core.config.logging_config import setup_logging
from app.transport.http.router import api_router
from app.transport.http.rate_limit import limiter, set_cooldown, get_retry_after
from app.domain.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
    UserNotFoundError,
    UserAlreadyExistsError,
)
from prometheus_fastapi_instrumentator import Instrumentator

setup_logging()


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    key = get_remote_address(request)
    set_cooldown(key)
    retry_after = get_retry_after(key) or settings.RATE_LIMIT_COOLDOWN_SECONDS
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded. Retry after {retry_after} seconds."},
        headers={"Retry-After": str(retry_after)},
    )


async def cooldown_middleware(request: Request, call_next):
    key = get_remote_address(request)
    retry_after = get_retry_after(key)
    if retry_after is not None:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit cooldown. Try again later."},
            headers={"Retry-After": str(retry_after)},
        )
    return await call_next(request)


async def request_duration_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_sec = time.perf_counter() - start
    client = get_remote_address(request)
    method = request.method
    path = request.url.path or ""
    status = response.status_code
    logging.getLogger("uvicorn.access").info(
        '%s - "%s %s" %s (%.3fs)',
        client,
        method,
        path,
        status,
        duration_sec,
    )
    return response


app.add_middleware(SlowAPIMiddleware)
app.middleware("http")(cooldown_middleware)
app.middleware("http")(request_duration_middleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)

Instrumentator().instrument(app).expose(app, tags=["metrics"])

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


# Map domain exceptions to HTTP (fallback if route did not map)
@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request, exc: InvalidCredentialsError):
    status_code = 401 if "Incorrect username" in str(exc) else 403
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


@app.exception_handler(InactiveUserError)
async def inactive_user_handler(request, exc: InactiveUserError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request, exc: UserNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request, exc: UserAlreadyExistsError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
