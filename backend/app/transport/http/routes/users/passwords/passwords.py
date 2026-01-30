from fastapi import APIRouter, HTTPException, status

from app.domain.exceptions import InvalidCredentialsError
from app.transport.http.routes.users.passwords.deps import PasswordUseCaseDep
from app.transport.schemas import Message, NewPassword

router = APIRouter(prefix="/passwords", tags=["passwords"])


@router.post("/recovery/{email}")
async def recover_password(
    password_use_case: PasswordUseCaseDep, email: str
) -> Message:
    await password_use_case.recover_password(email)
    return Message(message="If this email exists, you will receive a password reset link")


@router.post("/reset/")
async def reset_password(
    password_use_case: PasswordUseCaseDep, body: NewPassword
) -> Message:
    try:
        await password_use_case.reset_password(
            token=body.token,
            new_password=body.new_password,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Message(message="Password updated successfully")
