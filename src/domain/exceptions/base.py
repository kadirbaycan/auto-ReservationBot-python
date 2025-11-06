"""Base Domain Exceptions"""


class DomainException(Exception):
    """Base exception for domain layer errors."""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

    def to_dict(self) -> dict:
        """Convert exception to dictionary."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(DomainException):
    """Validation error exception."""

    def __init__(self, message: str, field: str = None, details: dict = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={**(details or {}), "field": field} if field else details,
        )
