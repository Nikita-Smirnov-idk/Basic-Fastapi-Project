from fastapi import Response

from app.core.config.config import settings

REFRESH_COOKIE_PATH=settings.API_V1_STR + "/users/auth"

def delete_cookie(response: Response, key: str, path: str = "/") -> Response:
    response.delete_cookie(
        key=key,
        path=path,
        secure=settings.IS_PROD,
        samesite="Lax",
    )
    return response


def set_cookie(
    *, response: Response, key: str, value: str, max_age: int, path: str = "/",
) -> Response:
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=settings.IS_PROD,
        samesite="Lax",
        max_age=max_age,
        path=path,
    )
    return response


def delete_refresh_from_cookie(response: Response) -> Response:
    return delete_cookie(response, "refresh_token", REFRESH_COOKIE_PATH)


def set_refresh_in_cookie(response: Response, refresh_token: str) -> Response:
    return set_cookie(
        response=response,
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=REFRESH_COOKIE_PATH,
    )


def delete_access_from_cookie(response: Response) -> Response:
    return delete_cookie(response, "access_token")


def set_access_in_cookie(response: Response, access_token: str) -> Response:
    return set_cookie(
        response=response,
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
