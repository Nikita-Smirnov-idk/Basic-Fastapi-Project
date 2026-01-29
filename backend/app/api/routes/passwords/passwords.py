from fastapi import APIRouter
from app.api.routes.passwords.deps import PasswordServiceDep
from app.models.general.models import Message
from app.models.users.models import NewPassword


router = APIRouter(prefix="/passwords", tags=["passwords"])

@router.post("/recovery/{email}")
async def recover_password(password_service: PasswordServiceDep, email: str) -> Message:
    """
    Password Recovery
    """
    await password_service.recover_password(email)
    return Message(message="If this email exists, you will receive a password reset link")


@router.post("/reset/")
async def reset_password(password_service: PasswordServiceDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    await password_service.reset_password(
        token=body.token,
        new_password=body.new_password
    )
    return Message(message="Password updated successfully")