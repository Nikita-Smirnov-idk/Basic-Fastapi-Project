import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.api.deps import UserAgentDep
from .deps import GoogleAuthServiceDep
from app.core.config import settings
from authlib.integrations.starlette_client import OAuth
from app.api import cookie

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/google-oauth", tags=["google-oauth"])

# Configure OAuth
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

@router.get("/login")
async def google_login(request: Request):
    """
    Инициация Google OAuth - редирект на Google
    """
    redirect_uri = f"{settings.BACKEND_HOST}/api/v1/google-oauth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(
    request: Request,
    google_auth_service: GoogleAuthServiceDep,
    user_agent: UserAgentDep,
):
    """
    Обработка callback от Google OAuth
    
    Правила связывания аккаунтов:
    - Если пользователь с таким google_id существует → логин
    - Если пользователь с таким email существует И есть hashed_password И is_verified=True → связываем
    - Если пользователь с таким email существует БЕЗ пароля ИЛИ БЕЗ верификации → ошибка
    - Если пользователя нет → создаем нового через Google (is_verified=True автоматически)
    """

    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo") or await oauth.google.parse_id_token(request, token)

        if not userinfo:
            raise HTTPException(status_code=400, detail="No userinfo from Google")

        google_id = userinfo["sub"]
        email = userinfo.get("email")
        full_name = userinfo.get("name")

        if not google_id or not email:
            raise HTTPException(status_code=400, detail="Missing required Google claims")

    except Exception as exc:
        logger.exception("Google OAuth flow failed")
        raise HTTPException(status_code=400, detail="Google authentication failed")

    tokens_data = await google_auth_service.process_google_oauth_callback(
        google_id=google_id,
        email=email,
        full_name=full_name,
        user_agent=user_agent,
    )
    # Устанавливаем refresh_token в HttpOnly cookie
    response = RedirectResponse(
        url=f"{settings.FRONTEND_HOST}/auth/callback?token={tokens_data["access_token"]}"
    )
    cookie.set_refresh_in_cookie(response, tokens_data["refresh_token"])

    return response