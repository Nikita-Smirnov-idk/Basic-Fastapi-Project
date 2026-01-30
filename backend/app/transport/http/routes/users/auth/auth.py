import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.domain.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
    UserAlreadyExistsError,
)
from app.transport.http import cookie
from app.transport.http.deps import CurrentUser, UserAgentDep
from app.transport.http.routes.users.auth.deps import AuthUseCaseDep, RefreshTokenDep
from app.transport.schemas import (
    BlockSessionRequest,
    CompleteSignupRequest,
    Message,
    SessionOut,
    SessionsListOut,
    StartSignupRequest,
    TokenResponse,
    UserPublic,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_domain_to_http(exc: Exception) -> None:
    if isinstance(exc, InvalidCredentialsError):
        if "Incorrect username" in str(exc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, InactiveUserError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, UserAlreadyExistsError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    raise exc


@router.post("/login", response_model=TokenResponse)
async def login(
    response: Response,
    auth_use_case: AuthUseCaseDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_agent: UserAgentDep = None,
) -> TokenResponse:
    try:
        data = await auth_use_case.login(
            form_data.username, password=form_data.password, user_agent=user_agent
        )
    except (InvalidCredentialsError, InactiveUserError) as e:
        _auth_domain_to_http(e)
    response = cookie.set_refresh_in_cookie(response, data["refresh_token"])
    logger.info("Login success, user_id=%s", data["user_id"])
    return TokenResponse(access_token=data["access_token"], token_type="bearer")


@router.post("/start-signup", status_code=status.HTTP_200_OK, response_model=Message)
async def start_signup(auth_use_case: AuthUseCaseDep, request: StartSignupRequest) -> Any:
    await auth_use_case.start_signup(request.email)
    return Message(message="If this email is not registered, you will receive a confirmation email")


@router.post("/complete-signup", response_model=UserPublic)
async def complete_signup(auth_use_case: AuthUseCaseDep, request: CompleteSignupRequest) -> Any:
    try:
        domain_user = await auth_use_case.complete_signup(
            request.token, request.password, request.full_name
        )
    except (InvalidCredentialsError, UserAlreadyExistsError) as e:
        _auth_domain_to_http(e)
    return UserPublic.model_validate(domain_user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    response: Response,
    auth_use_case: AuthUseCaseDep,
    refresh_token: RefreshTokenDep,
    user_agent: UserAgentDep,
):
    try:
        tokens = await auth_use_case.refresh(refresh_token, user_agent)
    except InvalidCredentialsError as e:
        cookie.delete_refresh_from_cookie(response)
        _auth_domain_to_http(e)
    response = cookie.set_refresh_in_cookie(response, tokens["refresh_token"])
    logger.info("Refresh rotation success, user_id=%s", tokens["user_id"])
    return TokenResponse(access_token=tokens["access_token"], token_type="bearer")


@router.post("/logout")
async def logout(
    response: Response,
    auth_use_case: AuthUseCaseDep,
    refresh_token: RefreshTokenDep,
):
    await auth_use_case.logout(refresh_token)
    response = cookie.delete_refresh_from_cookie(response)
    return Message(message="Logged out successfully")


@router.get("/my-sessions", response_model=SessionsListOut)
async def get_my_sessions(
    current_user: CurrentUser,
    auth_use_case: AuthUseCaseDep,
):
    sessions = await auth_use_case.get_sessions(str(current_user.id))
    session_outs = [SessionOut(**s) for s in sessions]
    return SessionsListOut(sessions=session_outs, total=len(session_outs))


@router.post("/block", status_code=status.HTTP_200_OK)
async def block_user_session(
    request: BlockSessionRequest,
    current_user: CurrentUser,
    auth_use_case: AuthUseCaseDep,
):
    try:
        await auth_use_case.block_session(str(current_user.id), request.family_id)
    except InvalidCredentialsError as e:
        _auth_domain_to_http(e)
    return Message(message="Session blocked successfully")


@router.post("/block/all", status_code=status.HTTP_200_OK)
async def block_all_sessions(
    auth_use_case: AuthUseCaseDep,
    current_user: CurrentUser,
):
    count = await auth_use_case.block_all_sessions(str(current_user.id))
    return Message(message="Have been blocked " + str(count) + " sessions")
