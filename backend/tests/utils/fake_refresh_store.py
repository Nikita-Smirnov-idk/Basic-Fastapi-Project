"""In-memory fake for IRefreshTokenStore. Used in tests to avoid Redis event loop conflicts with TestClient."""
from datetime import datetime
from typing import Any

from app.use_cases.ports.refresh_store import IRefreshTokenStore


class FakeRefreshStore(IRefreshTokenStore):
    """In-memory implementation for tests. Avoids Redis/event loop issues with Starlette TestClient."""

    FAMILY_PREFIX = "family:"
    USER_SESSIONS_PREFIX = "user_sessions:"

    def __init__(self) -> None:
        self._families: dict[str, dict] = {}
        self._user_sessions: dict[str, set[str]] = {}

    async def store_refresh_token(
        self,
        user_id: str,
        user_agent: str,
        jti: str,
        family_id: str,
    ) -> str:
        family_old_data = self._families.get(
            self.FAMILY_PREFIX + family_id
        )
        if not family_old_data:
            family_data = {
                "sub": user_id,
                "current_jti": jti,
                "user_agent": user_agent,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "blocked": False,
            }
        else:
            family_data = {
                "sub": family_old_data["sub"],
                "current_jti": jti,
                "user_agent": family_old_data["user_agent"],
                "created_at": family_old_data["created_at"],
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "blocked": family_old_data.get("blocked", False),
            }
        self._families[self.FAMILY_PREFIX + family_id] = family_data
        user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
        if user_sessions_key not in self._user_sessions:
            self._user_sessions[user_sessions_key] = set()
        self._user_sessions[user_sessions_key].add(family_id)
        return family_id

    async def get_family_data(self, family_id: str) -> dict[str, Any] | None:
        return self._families.get(self.FAMILY_PREFIX + family_id)

    async def block_family(self, family_id: str, user_id: str) -> None:
        user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
        if user_sessions_key in self._user_sessions:
            self._user_sessions[user_sessions_key].discard(family_id)
        key = self.FAMILY_PREFIX + family_id
        if key in self._families:
            self._families[key]["blocked"] = True

    async def is_family_blocked(self, family_id: str) -> bool:
        raw = self._families.get(self.FAMILY_PREFIX + family_id)
        if not raw:
            return False
        return raw.get("blocked", False) is True

    async def get_sessions_by_user_id(self, user_id: str) -> dict[str, Any]:
        user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
        family_ids = self._user_sessions.get(user_sessions_key, set())
        if not family_ids:
            return {}
        return {
            fid: self._families[self.FAMILY_PREFIX + fid]
            for fid in family_ids
            if self.FAMILY_PREFIX + fid in self._families
        }
