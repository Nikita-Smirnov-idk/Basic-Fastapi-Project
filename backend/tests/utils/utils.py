import random
import string

from fastapi.testclient import TestClient

from app.core.config.config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def get_superuser_token_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/users/auth/login", data=login_data)
    assert r.status_code == 200
    access_token = r.cookies.get("access_token")
    if not access_token:
        raise ValueError("Login did not set access_token cookie")
    return {"Cookie": f"access_token={access_token}"}
