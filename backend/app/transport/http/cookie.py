from fastapi import Response

from app.core.config.config import settings

def delete_cookie(response: Response, key: str) -> Response:
    response.delete_cookie(
        key=key,
        path="/",
        secure=settings.IS_PROD,
        samesite="Lax",
    )
    return response


def set_cookie(
    response: Response, key: str, value: str, max_age: int
) -> Response:
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=settings.IS_PROD,
        samesite="Lax",
        max_age=max_age,
        path="/",
    )
    return response


def delete_refresh_from_cookie(response: Response) -> Response:
    return delete_cookie(response, "refresh_token")


def set_refresh_in_cookie(response: Response, refresh_token: str) -> Response:
    return set_cookie(
        response,
        "refresh_token",
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
    )


def delete_access_from_cookie(response: Response) -> Response:
    return delete_cookie(response, "access_token")


def set_access_in_cookie(response: Response, access_token: str) -> Response:
    return set_cookie(
        response,
        "access_token",
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
