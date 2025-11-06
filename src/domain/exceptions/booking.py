"""Booking-related Domain Exceptions"""

from .base import DomainException


class BookingNotFoundError(DomainException):
    """Booking not found exception."""

    def __init__(self, booking_id: int = None, reference: str = None):
        identifier = f"ID {booking_id}" if booking_id else f"reference {reference}"
        super().__init__(
            message=f"Booking with {identifier} not found",
            code="BOOKING_NOT_FOUND",
            details={"booking_id": booking_id, "reference": reference},
        )


class BookingFailedError(DomainException):
    """Booking failed exception."""

    def __init__(self, message: str, reason: str = None):
        super().__init__(
            message=message,
            code="BOOKING_FAILED",
            details={"reason": reason} if reason else {},
        )


class MaxRetriesExceededError(DomainException):
    """Max retries exceeded exception."""

    def __init__(self, booking_id: int, attempts: int, max_attempts: int):
        super().__init__(
            message=f"Booking {booking_id} exceeded max retries ({attempts}/{max_attempts})",
            code="MAX_RETRIES_EXCEEDED",
            details={
                "booking_id": booking_id,
                "attempts": attempts,
                "max_attempts": max_attempts,
            },
        )
