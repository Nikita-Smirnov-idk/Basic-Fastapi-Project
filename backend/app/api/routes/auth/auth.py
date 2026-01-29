import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, UserAgentDep
from app.api.routes.auth.deps import AuthServiceDep, RefreshTokenDep

from app.models.users.models import (
    TokenResponse,
    UserPublic,
    SessionsListOut,
    BlockSessionRequest,
    StartSignupRequest,
    CompleteSignupRequest,
)
from app.models.general.models import Message
from app.api import cookie

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    auth_service: AuthServiceDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_agent: UserAgentDep,
):
    """
    Логин пользователя
    - username + password через form-data
    - возвращает access_token в теле + refresh_token в HttpOnly cookie
    """
    data = await auth_service.login(form_data.username, password=form_data.password, user_agent=user_agent)

    response = cookie.set_refresh_in_cookie(response, data["refresh_token"])
    logger.info("Login success, user_id=%s", data["user_id"])
    return TokenResponse(
        access_token=data["access_token"],
        token_type="bearer"
    )


@router.post("/start-signup", status_code=status.HTTP_200_OK, response_model=Message)
async def start_signup(auth_service: AuthServiceDep, request: StartSignupRequest) -> Any:
    """
    Начало регистрации - принимает email, проверяет валидность и уникальность,
    генерирует JWT токен и отправляет письмо для подтверждения регистрации.
    """
    await auth_service.start_signup(request.email)
    return Message(message="If this email is not registered, you will receive a confirmation email")


@router.post("/complete-signup", response_model=UserPublic)
async def complete_signup(auth_service: AuthServiceDep, request: CompleteSignupRequest) -> Any:
    """
    Завершение регистрации - принимает токен, пароль и имя,
    валидирует JWT токен, проверяет email в БД и создает пользователя.
    """
    return await auth_service.complete_signup(request.token, request.password, request.full_name)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    auth_service: AuthServiceDep,
    refresh_token: RefreshTokenDep,
    user_agent: UserAgentDep,
):
    """
    Обновление access-токена с помощью refresh-токена
    - refresh берётся из cookie (HttpOnly)
    - при успехе → новый access в теле + новый refresh в cookie (ротация)
    """
    try:
        tokens = await auth_service.refresh(refresh_token, user_agent)
    except Exception as exc:
        cookie.delete_refresh_from_cookie(response)
        raise exc
    
    response = cookie.set_refresh_in_cookie(response, tokens["refresh_token"])
    logger.info("Refresh rotation success, user_id=%s", tokens["user_id"])
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type="bearer"
    )


@router.post("/logout")
async def logout(
    response: Response,
    auth_service: AuthServiceDep,
    refresh_token: RefreshTokenDep,
):
    """
    Выход из системы — инвалидируем текущий refresh и всю family
    """
    await auth_service.logout(refresh_token)
    response = cookie.delete_refresh_from_cookie(response)
    return Message(message="Logged out successfully")

@router.get("/my-sessions", response_model=SessionsListOut)
async def get_my_sessions(
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    """
    Получить список всех активных сессий текущего пользователя
    (устройства/браузеры, где есть refresh-токены)
    """
    sessions = await auth_service.get_sessions(current_user.id)
    return SessionsListOut(
        sessions=sessions,
        total=len(sessions)
    )


@router.post("/block", status_code=status.HTTP_200_OK)
async def block_user_session(
    request: BlockSessionRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    """
    Заблокировать конкретную сессию (семью токенов) по family_id
    
    После этого все refresh-токены этой семьи станут невалидными
    (при попытке refresh -> ошибка)
    """
    await auth_service.block_session(current_user.id, request.family_id)
    return Message(message="Session blocked successfully")


@router.post("/block/all", status_code=status.HTTP_200_OK)
async def block_all_sessions(
    auth_service: AuthServiceDep,
    current_user: CurrentUser,
):
    """
    Принудительный логаут со всех устройств
    """
    count = await auth_service.block_all_sessions(current_user.id)
    return Message(message="Have been blocked " + str(count) + " sessions")