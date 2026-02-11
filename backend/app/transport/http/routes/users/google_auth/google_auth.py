import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth

from app.core.config.config import settings
from app.domain.exceptions import InvalidCredentialsError, InactiveUserError
from app.transport.http import cookie
from app.transport.http.deps import UserAgentDep
from app.transport.http.rate_limit import limiter, PER_ROUTE_LIMIT
from app.transport.http.routes.users.google_auth.deps import GoogleAuthUseCaseDep

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/google-oauth", tags=["google-oauth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login")
@limiter.limit(PER_ROUTE_LIMIT)
async def google_login(request: Request):
    redirect_uri = f"{settings.BACKEND_HOST}{settings.API_V1_STR}/users/google-oauth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
@limiter.limit(PER_ROUTE_LIMIT)
async def google_callback(
    request: Request,
    google_auth_use_case: GoogleAuthUseCaseDep,
    user_agent: UserAgentDep,
):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo") or await oauth.google.parse_id_token(request, token)
        if not userinfo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No userinfo from Google")
        google_id = userinfo["sub"]
        email = userinfo.get("email")
        full_name = userinfo.get("name")
        if not google_id or not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required Google claims")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Google OAuth flow failed")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google authentication failed")

    try:
        tokens_data = await google_auth_use_case.process_google_oauth_callback(
            google_id=google_id,
            email=email,
            full_name=full_name,
            user_agent=user_agent,
        )
    except (InvalidCredentialsError, InactiveUserError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    response = RedirectResponse(
        url=f"{settings.FRONTEND_HOST}/users/me"
    )
    cookie.set_access_in_cookie(response, tokens_data["access_token"])
    cookie.set_refresh_in_cookie(response, tokens_data["refresh_token"])
    return response
