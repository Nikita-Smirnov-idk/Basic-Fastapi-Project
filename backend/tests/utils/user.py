from fastapi.testclient import TestClient
from sqlmodel import Session

from app.config import settings
from app.infrastructure.persistence.models import User
from app.infrastructure.users.sync_helpers import (
    create_user_sync,
    get_user_by_email_sync,
    update_user_sync,
)
from tests.utils.utils import random_email, random_lower_string


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/users/auth/login", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> User:
    email = random_email()
    password = random_lower_string()
    user = create_user_sync(session=db, email=email, password=password)
    return user


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """
    Return a valid token for the user with given email.
    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    user = get_user_by_email_sync(session=db, email=email)
    if not user:
        user = create_user_sync(session=db, email=email, password=password)
    else:
        user = update_user_sync(session=db, db_user=user, data={"password": password})
    return user_authentication_headers(client=client, email=email, password=password)
