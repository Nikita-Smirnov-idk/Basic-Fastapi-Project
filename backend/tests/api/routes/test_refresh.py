"""Tests for refresh token endpoint: security scenarios (different agent, blocked token, blocked family)."""
from fastapi.testclient import TestClient

from app.core.config.config import settings
from app.infrastructure.jwt.token_service import TokenService
from tests.utils.utils import get_superuser_token_headers
import time


def test_refresh_different_agent_invalidates_family(client: TestClient) -> None:
    """Refresh with different User-Agent -> 403 and family invalidated."""
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    login_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/login",
        data=login_data,
        headers={"User-Agent": "Chrome/1.0"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.cookies.get("refresh_token")
    assert refresh_token

    # Different agent -> must fail and invalidate family
    refresh_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "Firefox/2.0"},
        cookies={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 403

    client.cookies.clear()

    # Token is now blocked; retry must also fail
    retry_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "Chrome/1.0"},
        cookies={"refresh_token": refresh_token},
    )
    assert retry_resp.status_code == 403


def test_refresh_blocked_token_invalidates_family(client: TestClient) -> None:
    """Using a blocked (already rotated) refresh token -> 403 and family invalidated."""
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    login_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/login",
        data=login_data,
        headers={"User-Agent": "AgentA"},
    )
    assert login_resp.status_code == 200
    old_refresh = login_resp.cookies.get("refresh_token")
    assert old_refresh

    # Successful refresh rotates token and blocks the old one
    first_refresh = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "AgentA"},
        cookies={"refresh_token": old_refresh},
    )
    assert first_refresh.status_code == 200

    client.cookies.clear()

    # Reusing blocked token must fail
    second_refresh = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "AgentA"},
        cookies={"refresh_token": old_refresh},
    )
    assert second_refresh.status_code == 403


def test_refresh_family_blocked_no_pass(client: TestClient) -> None:
    """When family is blocked, refresh must not succeed."""
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    login_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/login",
        data=login_data,
        headers={"User-Agent": "AgentX"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.cookies.get("refresh_token")
    access_token = login_resp.cookies.get("access_token")
    assert refresh_token and access_token

    token_service = TokenService()
    payload = token_service.decode_and_validate(refresh_token, "refresh")
    family_id = token_service.get_family_id(payload)

    # Get sessions and check that family_id from token payload is in my_sessions
    sessions_resp = client.get(
        f"{settings.API_V1_STR}/users/auth/my-sessions",
    )
    assert sessions_resp.status_code == 200
    my_sessions = sessions_resp.json()
    session_family_ids = [s["family_id"] for s in my_sessions["sessions"]]
    assert family_id in session_family_ids, f"family_id {family_id} from token payload must be in my_sessions: {session_family_ids}"

    # Block this session (family)
    block_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/block",
        json={"family_id": family_id},
    )
    assert block_resp.status_code == 200

    # Refresh with blocked family must fail
    refresh_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "AgentX"},
    )
    assert refresh_resp.status_code == 403


def test_refresh_success_same_agent(client: TestClient) -> None:
    """Refresh with same User-Agent -> success and new tokens."""
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    login_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/login",
        data=login_data,
        headers={"User-Agent": "Safari/1.0"},
    )
    assert login_resp.status_code == 200

    refresh_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "Safari/1.0"},
    )
    assert refresh_resp.status_code == 200
    assert refresh_resp.cookies.get("access_token")
    assert refresh_resp.cookies.get("refresh_token")
    assert refresh_resp.json() == {"message": "Access token updated successfully"}


def test_refresh_invalid_token(client: TestClient) -> None:
    """Refresh with invalid/malformed token -> 403."""
    refresh_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "TestAgent"},
        cookies={"refresh_token": "invalid.or.fake.jwt"},
    )
    assert refresh_resp.status_code == 403


def test_refresh_no_token(client: TestClient) -> None:
    """Refresh without refresh_token cookie -> 403 or 401."""
    refresh_resp = client.post(
        f"{settings.API_V1_STR}/users/auth/refresh",
        headers={"User-Agent": "TestAgent"},
    )
    assert refresh_resp.status_code in (401, 403)
