"""Domain exceptions: business rule violations and domain errors."""


class DomainException(Exception):
    """Base for domain-level errors."""

    pass


class UserNotFoundError(DomainException):
    """User not found by id or email."""

    pass


class InvalidCredentialsError(DomainException):
    """Invalid email/password or token."""

    pass


class UserAlreadyExistsError(DomainException):
    """User with this email already exists."""

    pass


class InactiveUserError(DomainException):
    """User account is inactive."""

    pass


class AdminCannotBeDeletedError(DomainException):
    """Admin is not allowed to delete their own account."""

    pass
