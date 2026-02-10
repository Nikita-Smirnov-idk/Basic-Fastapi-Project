from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config.config import settings
from app.core.config.db import engine, init_db
from app.main import app
from app.domain.entities.db.user import User
from app.transport.http.deps import get_redis_repo
from tests.utils.fake_refresh_store import FakeRefreshStore
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers

_fake_refresh_store = FakeRefreshStore()


def _get_fake_redis_repo():
    return _fake_refresh_store


@pytest.fixture(scope="session", autouse=True)
def override_redis() -> Generator[None, None, None]:
    """Replace Redis with in-memory fake to avoid event loop conflicts with TestClient."""
    app.dependency_overrides[get_redis_repo] = _get_fake_redis_repo
    yield
    app.dependency_overrides.pop(get_redis_repo, None)


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client(override_redis: None) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
