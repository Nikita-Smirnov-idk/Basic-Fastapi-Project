from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse

from app.services.users import crud
from app.api.deps import SessionDep, RedisDep, get_user_agent
from app.services.jwt import tokens
from app.core.config import settings
from app.services.redis import utils as redis_utils
from authlib.integrations.starlette_client import OAuth

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
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(
    request: Request,
    session: SessionDep,
    redis: RedisDep,
    user_agent: str = Depends(get_user_agent),
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
        # Обмен кода на токен и получение userinfo через authlib
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get("userinfo")
        
        # Если userinfo нет в токене, парсим id_token
        if not userinfo:
            userinfo = await oauth.google.parse_id_token(request, token)
        
        if not userinfo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google authentication failed",
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed",
        )

    google_id = userinfo.get("sub")  # В OIDC используется "sub", а не "id"
    email = userinfo.get("email")
    full_name = userinfo.get("name")

    if not google_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication failed",
        )

    # Поиск пользователя по google_id
    user = crud.get_user_by_google_id(session=session, google_id=google_id)
    
    if not user:
        # Проверяем, есть ли пользователь с таким email
        existing_user = crud.get_user_by_email(session=session, email=email)
        if existing_user:
            # Связывание возможно только если:
            # 1. У пользователя есть пароль (hashed_password)
            # 2. Email верифицирован (is_verified=True)
            if not existing_user.hashed_password:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Failed to authenticate",
                )
            
            if not existing_user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This account was registered by another authentication method."+
                    "Please verify your email first, to link your google account",
                )
            
            # Связываем аккаунты: добавляем google_id к существующему пользователю
            user = crud.link_google_id(session, existing_user, google_id)
        else:
            # Создаем нового пользователя через Google
            # Для Google аккаунтов email считается верифицированным автоматически
            user = crud.create_user_by_google_id(
                session=session,
                email=email,
                google_id=google_id,
                full_name=full_name,
            )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Создаем токены
    access_token = tokens.create_access_token(data={"sub": str(user.id)})
    refresh_token = tokens.create_refresh_token(data={"sub": str(user.id)})

    # Сохраняем refresh в Redis
    _ = await redis_utils.store_refresh_token(
        redis_client=redis,
        user_id=user.id,
        refresh_token=refresh_token,
        user_agent=user_agent,
    )

    # Устанавливаем refresh_token в HttpOnly cookie
    response = RedirectResponse(
        url=f"{settings.FRONTEND_HOST}/auth/callback?token={access_token}"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "local",
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )

    return response