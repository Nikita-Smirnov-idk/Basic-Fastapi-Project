"""Helper: create access/refresh tokens and store refresh in store. Uses ports only."""
from typing import Any
import uuid

from app.use_cases.ports.refresh_store import IRefreshTokenStore
from app.use_cases.ports.token_service import ITokenService


async def create_and_store_tokens(
    token_service: ITokenService,
    refresh_store: IRefreshTokenStore,
    user_id: str,
    user_agent: str,
    family_id: str | None = None,
) -> dict[str, Any]:
    """Create access + refresh tokens, store refresh in store. Returns dict with access_token, refresh_token, user_id."""
    if not family_id:
        family_id = str(uuid.uuid4())
    jti = str(uuid.uuid4())
    
    access_token = token_service.create_access_token(
        {
            "sub": str(user_id)
        }
    )
    refresh_token = token_service.create_refresh_token(
        {
            "sub": str(user_id),
            "family_id": str(family_id), 
            "jti": str(jti)
        }
    )

    await refresh_store.store_refresh_token(
        user_id=str(user_id),
        user_agent=user_agent,
        jti=jti,
        family_id=family_id,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user_id,
    }
