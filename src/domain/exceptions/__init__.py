"""Domain Exceptions - Business Logic Errors"""

from .base import DomainException, ValidationError
from .client import ClientNotFoundError, ClientAlreadyExistsError, InvalidClientDataError
from .booking import BookingNotFoundError, BookingFailedError, MaxRetriesExceededError
from .appointment import AppointmentNotFoundError, NoSlotsAvailableError

__all__ = [
    # Base
    "DomainException",
    "ValidationError",
    # Client
    "ClientNotFoundError",
    "ClientAlreadyExistsError",
    "InvalidClientDataError",
    # Booking
    "BookingNotFoundError",
    "BookingFailedError",
    "MaxRetriesExceededError",
    # Appointment
    "AppointmentNotFoundError",
    "NoSlotsAvailableError",
]
