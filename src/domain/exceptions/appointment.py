"""Appointment-related Domain Exceptions"""

from .base import DomainException


class AppointmentNotFoundError(DomainException):
    """Appointment not found exception."""

    def __init__(self, appointment_id: int = None, reference: str = None):
        identifier = f"ID {appointment_id}" if appointment_id else f"reference {reference}"
        super().__init__(
            message=f"Appointment with {identifier} not found",
            code="APPOINTMENT_NOT_FOUND",
            details={"appointment_id": appointment_id, "reference": reference},
        )


class NoSlotsAvailableError(DomainException):
    """No appointment slots available exception."""

    def __init__(self, location: str = None, date: str = None):
        message = "No appointment slots available"
        if location:
            message += f" at {location}"
        if date:
            message += f" on {date}"

        super().__init__(
            message=message,
            code="NO_SLOTS_AVAILABLE",
            details={"location": location, "date": date},
        )
