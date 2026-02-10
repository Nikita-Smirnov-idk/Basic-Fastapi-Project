# Domain entities: pure business objects, no DB/ORM.
from app.domain.entities.pydantic.user import User as DomainUser

__all__ = ["DomainUser"]
