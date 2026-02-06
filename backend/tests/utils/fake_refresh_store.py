"""In-memory fake for IRefreshTokenStore. Used in tests to avoid Redis event loop conflicts with TestClient."""
import hashlib
import uuid
from datetime import datetime
from typing import Any

from app.core.config.config import settings
from app.use_cases.ports.refresh_store import IRefreshTokenStore


class FakeRefreshStore(IRefreshTokenStore):
    """In-memory implementation for tests. Avoids Redis/event loop issues with Starlette TestClient."""

    REFRESH_PREFIX = "refresh:"
    FAMILY_PREFIX = "family:"
    REFRESH_BLOCKLIST_PREFIX = "refresh_block:"
    USER_SESSIONS_PREFIX = "user_sessions:"
    TOKEN_PEPPER = settings.TOKEN_PEPPER
    EXPIRE_TIME = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400

    def __init__(self) -> None:
        self._refresh: dict[str, dict] = {}
        self._families: dict[str, dict] = {}
        self._blocked: set[str] = {}
        self._user_sessions: dict[str, set[str]] = {}

    @classmethod
    def hash_refresh_token(cls, token: str) -> str:
        input_bytes = (token + cls.TOKEN_PEPPER).encode("utf-8")
        return hashlib.sha256(input_bytes).hexdigest()

    async def store_refresh_token(
        self,
        user_id: str,
        refresh_token: str,
        user_agent: str,
        family_id: str | None = None,
    ) -> str:
        if not family_id:
            family_id = str(uuid.uuid4())
            family_data = {
                "user_agent": user_agent,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "blocked": False,
            }
        else:
            family_old_data = self._families.get(self.FAMILY_PREFIX + family_id)
            if family_old_data is None:
                raise ValueError("Invalid token")
            family_data = {
                "user_agent": family_old_data["user_agent"],
                "created_at": family_old_data["created_at"],
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "blocked": family_old_data.get("blocked", False),
            }
        token_hash = self.hash_refresh_token(refresh_token)
        self._families[self.FAMILY_PREFIX + family_id] = family_data
        user_sessions_key = self.USER_SESSIONS_PREFIX + user_id
        if user_sessions_key not in self._user_sessions:
            self._user_sessions[user_sessions_key] = set()
        self._user_sessions[user_sessions_key].add(family_id)
        data = {
            "user_id": user_id,
            "user_agent": user_agent,
            "family_id": family_id,
        }
        self._refresh[self.REFRESH_PREFIX + token_hash] = data
        return family_id

    async def get_refresh_data(self, refresh_token: str) -> dict[str, Any] | None:
        token_hash = self.hash_refresh_token(refresh_token)
        return self._refresh.get(self.REFRESH_PREFIX + token_hash)

    async def block_refresh(self, token: str) -> None:
        token_hash = self.hash_refresh_token(token)
        self._blocked.add(self.REFRESH_BLOCKLIST_PREFIX + token_hash)

    async def try_block_refresh(self, token: str) -> bool:
        token_hash = self.hash_refresh_token(token)
        key = self.REFRESH_BLOCKLIST_PREFIX + token_hash
        if key in self._blocked:
            return False
        self._blocked.add(key)
        return True

    async def is_refresh_blocked(self, token: str) -> bool:
        token_hash = self.hash_refresh_token(token)
        return (self.REFRESH_BLOCKLIST_PREFIX + token_hash) in self._blocked

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
