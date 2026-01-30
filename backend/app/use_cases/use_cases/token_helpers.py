"""Helper: create access/refresh tokens and store refresh in store. Uses ports only."""
from typing import Any

from app.use_cases.ports.refresh_store import IRefreshTokenStore
from app.use_cases.ports.token_service import ITokenService


async def create_and_store_tokens(
    token_service: ITokenService,
    refresh_store: IRefreshTokenStore,
    user_id: str,
    user_agent: str,
) -> dict[str, Any]:
    """Create access + refresh tokens, store refresh in store. Returns dict with access_token, refresh_token, user_id."""
    access_token = token_service.create_access_token({"sub": str(user_id)})
    refresh_token = token_service.create_refresh_token({"sub": str(user_id)})
    await refresh_store.store_refresh_token(
        user_id=str(user_id),
        refresh_token=refresh_token,
        user_agent=user_agent,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user_id,
    }
