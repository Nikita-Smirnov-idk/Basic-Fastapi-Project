import uuid
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config.config import settings
from app.domain.entities.db.user import User
from app.infrastructure.jwt.token_service import TokenService
from app.infrastructure.passwords.utils import verify_password
from app.infrastructure.users.sync_helpers import (
    create_user_sync,
    get_user_by_email_sync,
)
from tests.utils.utils import random_email, random_lower_string


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"]
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    assert current_user["email"] == settings.EMAIL_TEST_USER


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    r = client.post(
        f"{settings.API_V1_STR}/admin/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = get_user_by_email_sync(session=db, email=username)
    assert user
    assert user.email == created_user["email"]


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user = create_user_sync(
        session=db, email=username, password=password, full_name=full_name
    )
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/admin/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = get_user_by_email_sync(session=db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


def test_get_existing_user_current_user(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user = create_user_sync(
        session=db, email=username, password=password, full_name=full_name
    )
    user_id = user.id

    login_data = {"username": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/auth/login", data=login_data
    )
    assert r.status_code == 200
    access_token = r.cookies.get("access_token")
    headers = {"Cookie": f"access_token={access_token}"}

    r = client.get(
        f"{settings.API_V1_STR}/admin/{user_id}",
        headers=headers,
    )
    assert r.status_code == 403


def test_get_existing_user_permissions_error(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/admin/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json() == {"detail": "The user doesn't have enough privileges"}


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    create_user_sync(
        session=db, email=username, password=password, full_name=full_name
    )
    data = {"email": username, "password": password, "full_name": full_name}
    r = client.post(
        f"{settings.API_V1_STR}/admin/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    data = {"email": username, "password": password, "full_name": full_name}
    r = client.post(
        f"{settings.API_V1_STR}/admin/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    create_user_sync(
        session=db, email=username, password=password, full_name=random_lower_string()
    )

    username2 = random_email()
    password2 = random_lower_string()
    create_user_sync(
        session=db, email=username2, password=password2, full_name=random_lower_string()
    )

    r = client.get(f"{settings.API_V1_STR}/admin/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "email" in item


def test_register_user(client: TestClient, db: Session) -> None:
    """Signup via start-signup + complete-signup (token created in test)."""
    username = random_email()
    password = random_lower_string()
    full_name = random_lower_string()

    token_service = TokenService()
    token = token_service.create_signup_token(
        {"sub": username, "full_name": full_name}
    )

    data = {"token": token, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/auth/complete-signup",
        json=data,
    )
    assert r.status_code == 200
    created_user = r.json()
    assert created_user["email"] == username
    assert created_user["full_name"] == full_name

    user_query = select(User).where(User.email == username)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == username
    assert user_db.full_name == full_name
    assert verify_password(password, user_db.hashed_password)


def test_register_user_already_exists_error(client: TestClient, db: Session) -> None:
    """Complete signup with email that already exists (superuser)."""
    password = random_lower_string()
    full_name = random_lower_string()

    token_service = TokenService()
    token = token_service.create_signup_token(
        {"sub": settings.FIRST_SUPERUSER, "full_name": full_name}
    )

    data = {"token": token, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/auth/complete-signup",
        json=data,
    )
    assert r.status_code == 400
    assert "already exists" in r.json()["detail"].lower()


def test_delete_user_me(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user = create_user_sync(
        session=db, email=username, password=password, full_name=random_lower_string()
    )
    user_id = user.id

    login_data = {"username": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/auth/login", data=login_data
    )
    assert r.status_code == 200
    access_token = r.cookies.get("access_token")
    headers = {"Cookie": f"access_token={access_token}"}

    r = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
    )
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None


def test_delete_user_me_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    response = r.json()
    assert response["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_super_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user = create_user_sync(
        session=db, email=username, password=password, full_name=random_lower_string()
    )
    user_id = user.id
    r = client.delete(
        f"{settings.API_V1_STR}/admin/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None


def test_delete_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/admin/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


def test_delete_user_current_super_user_error(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    super_user = get_user_by_email_sync(session=db, email=settings.FIRST_SUPERUSER)
    assert super_user
    user_id = super_user.id

    r = client.delete(
        f"{settings.API_V1_STR}/admin/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_without_privileges(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user = create_user_sync(
        session=db, email=username, password=password, full_name=random_lower_string()
    )

    r = client.delete(
        f"{settings.API_V1_STR}/admin/{user.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "The user doesn't have enough privileges"
