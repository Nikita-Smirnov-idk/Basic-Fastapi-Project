from fastapi import Response
from app.core.config import settings


def delete_refresh_from_cookie(response: Response) -> Response:
    response.delete_cookie(
        key="refresh_token",
        path="/",
        secure=settings.IS_PROD,
        samesite="Lax",
    )

    return response

def set_refresh_in_cookie(response: Response, refresh_token: str) -> Response:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.IS_PROD,
        samesite="Lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )
    
    return response