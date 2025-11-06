"""Client-related Domain Exceptions"""

from .base import DomainException


class ClientNotFoundError(DomainException):
    """Client not found exception."""

    def __init__(self, client_id: int = None, email: str = None):
        identifier = f"ID {client_id}" if client_id else f"email {email}"
        super().__init__(
            message=f"Client with {identifier} not found",
            code="CLIENT_NOT_FOUND",
            details={"client_id": client_id, "email": email},
        )


class ClientAlreadyExistsError(DomainException):
    """Client already exists exception."""

    def __init__(self, email: str):
        super().__init__(
            message=f"Client with email {email} already exists",
            code="CLIENT_ALREADY_EXISTS",
            details={"email": email},
        )


class InvalidClientDataError(DomainException):
    """Invalid client data exception."""

    def __init__(self, message: str, field: str = None):
        super().__init__(
            message=message,
            code="INVALID_CLIENT_DATA",
            details={"field": field} if field else {},
        )
