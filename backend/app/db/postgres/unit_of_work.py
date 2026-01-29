from app.db.postgres.repositories.users.user_repository import UserRepository
from app.db.postgres.session import get_async_session


class UnitOfWork:
    users: UserRepository

    async def __aenter__(self) -> "UnitOfWork":
        self._session = await get_async_session()
        self.users = UserRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
