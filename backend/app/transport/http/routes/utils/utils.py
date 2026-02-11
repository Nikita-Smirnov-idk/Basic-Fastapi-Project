from fastapi import APIRouter, Request

from app.transport.http.rate_limit import limiter, PER_ROUTE_LIMIT

router = APIRouter(prefix="/utils", tags=["utils"])


@router.get("/health-check/")
@limiter.limit(PER_ROUTE_LIMIT)
async def health_check(request: Request) -> bool:
    return True
