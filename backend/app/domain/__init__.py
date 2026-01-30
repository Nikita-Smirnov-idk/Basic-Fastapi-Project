"""
Domain layer: entities, value objects, exceptions.
No dependencies on outer layers (application, infrastructure, transport).
"""
from app.domain.entities import DomainUser, DomainItem
from app.domain.exceptions import (
    DomainException,
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InactiveUserError,
)
from app.domain.value_objects import UserId, Email

__all__ = [
    "DomainUser",
    "DomainItem",
    "DomainException",
    "UserNotFoundError",
    "InvalidCredentialsError",
    "UserAlreadyExistsError",
    "InactiveUserError",
    "UserId",
    "Email",
]
