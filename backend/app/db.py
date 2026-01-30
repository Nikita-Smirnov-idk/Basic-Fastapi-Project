"""Sync DB engine and init_db for scripts (initial_data, tests). Async session in infrastructure.persistence.postgres."""
from sqlmodel import Session, create_engine, select

from app.config import settings
from app.infrastructure.persistence.models import User
from app.infrastructure.users.sync_helpers import create_user_sync

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    """Create first superuser if not exists. Uses sync session (for initial_data/scripts)."""
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        create_user_sync(
            session,
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
