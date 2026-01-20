from typing import Annotated, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.services.users import crud
from app.api.deps import CurrentUser, SessionDep, RedisDep, CurrentRefreshToken, get_user_agent
from app.services.jwt import tokens
import app.services.redis.utils as redis_storage
from app.core.config import settings
from app.services.redis import utils as redis_utils

from app.models.users.models import (
    TokenResponse,
    UserCreate,
    UserPublic,
    UserRegister,
    SessionOut,
    SessionsListOut,
    BlockSessionRequest,
    StartSignupRequest,
    CompleteSignupRequest,
)
from app.models.general.models import Message
from app.utils import generate_signup_confirmation_email, send_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    session: SessionDep,
    redis: RedisDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_agent: str = Depends(get_user_agent),
    response: Response = None,
):
    """
    Логин пользователя
    - username + password через form-data
    - возвращает access_token в теле + refresh_token в HttpOnly cookie
    """
    user = crud.authenticate(session=session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = tokens.create_access_token(data={"sub": str(user.id)})
    refresh_token = tokens.create_refresh_token(data={"sub": str(user.id)})

    # Сохраняем refresh в Redis с family_id
    _ = await redis_storage.store_refresh_token(
        redis_client=redis,
        user_id=user.id,
        refresh_token=refresh_token,
        user_agent=user_agent,
    )

    # Устанавливаем refresh_token в HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "local",
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )


@router.post("/start-signup", status_code=status.HTTP_200_OK, response_model=Message)
def start_signup(session: SessionDep, request: StartSignupRequest) -> Any:
    """
    Начало регистрации - принимает email, проверяет валидность и уникальность,
    генерирует JWT токен и отправляет письмо для подтверждения регистрации.
    """
    # Проверяем, что email не занят
    existing_user = crud.get_user_by_email(session=session, email=request.email)
    if existing_user:
        # Для безопасности не раскрываем, что пользователь существует
        # Возвращаем успех в любом случае, чтобы не сливать информацию о зарегистрированных email
        return Message(message="If this email is not registered, you will receive a confirmation email")
    
    # Генерируем JWT токен для регистрации
    signup_token = tokens.create_signup_token(data={"sub": request.email})
    
    # Генерируем и отправляем письмо с подтверждением
    if settings.emails_enabled:
        email_data = generate_signup_confirmation_email(
            email=request.email,
            token=signup_token
        )
        send_email(
            email_to=request.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    else:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Signup token for {request.email}: {signup_token}")
    
    # Возвращаем успех (не раскрываем, зарегистрирован email или нет)
    return Message(message="If this email is not registered, you will receive a confirmation email")


@router.post("/complete-signup", response_model=UserPublic)
def complete_signup(session: SessionDep, request: CompleteSignupRequest) -> Any:
    """
    Завершение регистрации - принимает токен, пароль и имя,
    валидирует JWT токен, проверяет email в БД и создает пользователя.
    """
    # Валидируем JWT токен
    try:
        payload = tokens.decode_token(request.token)
        
        # Проверяем тип токена
        if payload.get("type") != "signup":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        # Извлекаем email из токена
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        # Проверяем issuer
        if payload.get("iss") != settings.FRONTEND_HOST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    
    # Проверяем, что пользователь с таким email еще не существует
    existing_user = crud.get_user_by_email(session=session, email=email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Создаем пользователя
    user_create = UserCreate(
        email=email,
        password=request.password,
        full_name=request.full_name,
        is_verified=True
    )
    # После подтверждения email считаем пользователя верифицированным
    user = crud.create_user_by_password(session=session, user_create=user_create)
    return user

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    redis: RedisDep,
    refresh_token: CurrentRefreshToken,
    user_agent: str = Depends(get_user_agent),
    response: Response = None,
):
    """
    Обновление access-токена с помощью refresh-токена
    - refresh берётся из cookie (HttpOnly)
    - при успехе → новый access в теле + новый refresh в cookie (ротация)
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    try:
        payload = tokens.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type: refresh token required",
            )
        user_id = str(payload.get("sub"))
        if user_id is None:
            raise ValueError("Invalid token payload")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}"
        )

    # Проверки безопасности (ротация + blocklist + user-agent + family block)
    refresh_data = await redis_utils.get_refresh_data(redis, refresh_token)

    if not refresh_data:
        raise HTTPException(status_code=403, detail="Invalid Token")

    if str(refresh_data["user_id"]) != user_id:
        raise HTTPException(status_code=403, detail="Invalid Token")

    if refresh_data["user_agent"] != user_agent:
        await redis_utils.block_family(redis, refresh_data["family_id"])
        raise HTTPException(status_code=403, detail="Invalid Token")

    if await redis_utils.is_refresh_blocked(redis, refresh_token):
        if "family_id" in refresh_data:
            await redis_utils.block_family(redis, refresh_data["family_id"], user_id)
        raise HTTPException(status_code=403, detail="Invalid Token")

    if await redis_utils.is_family_blocked(redis, refresh_data["family_id"]):
        raise HTTPException(status_code=403, detail="Invalid Token")

    # Всё прошло → ротация
    await redis_utils.block_refresh(redis, refresh_token)  # старый → в blacklist

    new_access_token = tokens.create_access_token(data={"sub": str(user_id)})
    new_refresh_token = tokens.create_refresh_token(data={"sub": str(user_id)})

    # Сохраняем новый refresh с тем же family_id
    await redis_utils.store_refresh_token(
        redis_client=redis,
        user_id=user_id,
        refresh_token=new_refresh_token,
        user_agent=user_agent,
        family_id=refresh_data["family_id"],
    )

    # Новый cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "local",
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,  # можно убрать
        token_type="bearer"
    )

@router.post("/logout")
async def logout(
    redis: RedisDep,
    refresh_token: CurrentRefreshToken,
):
    """
    Выход из системы — инвалидируем текущий refresh и всю family
    """
    if not refresh_token:
        return Message(message= "No active session")

    refresh_data = await redis_utils.get_refresh_data(redis, refresh_token)

    if refresh_data:
        await redis_utils.block_refresh(redis, refresh_token)
        if "family_id" in refresh_data:
            await redis_utils.block_family(redis, refresh_data["family_id"], refresh_data["user_id"])

    # Можно очистить cookie
    response = Response()
    response.delete_cookie(key="refresh_token", path="/")

    return Message(message="Logged out successfully")

@router.get("/my-sessions", response_model=SessionsListOut)
async def get_my_sessions(
    current_user: CurrentUser,
    redis_client: RedisDep,
):
    """
    Получить список всех активных сессий текущего пользователя
    (устройства/браузеры, где есть refresh-токены)
    """
    sessions_dict: Dict[str, dict] = await redis_utils.get_sessions_by_user_id(
        redis_client, str(current_user.id)
    )

    active_sessions = []
    for family_id, data in sessions_dict.items():
        # фильтруем заблокированные или истёкшие (если expired — redis сам удалит)
        if not data.get("blocked", False):
            active_sessions.append(
                SessionOut(
                    family_id=family_id,
                    user_agent=data.get("user_agent", "Unknown"),
                    created_at=data.get("created_at", ""),
                    last_active=data.get("last_active", ""),
                )
            )

    # Можно сортировать, например, по last_active DESC
    active_sessions.sort(key=lambda x: x.last_active, reverse=True)

    return SessionsListOut(
        sessions=active_sessions,
        total=len(active_sessions)
    )


@router.post("/block", status_code=status.HTTP_200_OK)
async def block_user_session(
    request: BlockSessionRequest,
    current_user: CurrentUser,
    redis_client: RedisDep,
):
    """
    Заблокировать конкретную сессию (семью токенов) по family_id
    
    После этого все refresh-токены этой семьи станут невалидными
    (при попытке refresh -> ошибка)
    """
    family_id = request.family_id.strip()

    # Проверяем, принадлежит ли эта сессия текущему пользователю
    sessions = await redis_utils.get_sessions_by_user_id(redis_client, str(current_user.id))
    if family_id not in sessions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This session does not belong to you"
        )

    # Блокируем
    await redis_utils.block_family(redis_client, family_id, str(current_user.id))

    return Message(message = "Session blocked successfully")


@router.post("/block/all", status_code=status.HTTP_200_OK)
async def block_all_sessions_except_current(
    current_user: CurrentUser,
    redis_client: RedisDep,
):
    """
    Принудительный логаут со всех устройств
    """
    sessions_dict = await redis_utils.get_sessions_by_user_id(redis_client, str(current_user.id))

    blocked_count = 0

    for family_id in list(sessions_dict.keys()):
        await redis_utils.block_family(redis_client, family_id, str(current_user.id))
        blocked_count += 1

    return Message(
        message = "Have been blocked " + str(blocked_count) + " sessions" 
    )