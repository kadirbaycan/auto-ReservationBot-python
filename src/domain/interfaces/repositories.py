"""Repository Interfaces - Database Access Contracts"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from src.domain.models import Client, Booking, Appointment, AppointmentSlot


class IClientRepository(ABC):
    """Client repository interface."""

    @abstractmethod
    async def create(self, client: Client) -> Client:
        """Create a new client."""
        pass

    @abstractmethod
    async def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Client]:
        """Get client by email."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Client]:
        """Get all clients with pagination."""
        pass

    @abstractmethod
    async def update(self, client: Client) -> Client:
        """Update existing client."""
        pass

    @abstractmethod
    async def delete(self, client_id: int, soft: bool = True) -> bool:
        """Delete client (soft or hard delete)."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if client exists by email."""
        pass


class IBookingRepository(ABC):
    """Booking repository interface."""

    @abstractmethod
    async def create(self, booking: Booking) -> Booking:
        """Create a new booking."""
        pass

    @abstractmethod
    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID."""
        pass

    @abstractmethod
    async def get_by_reference(self, reference: str) -> Optional[Booking]:
        """Get booking by reference number."""
        pass

    @abstractmethod
    async def get_by_client(self, client_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings for a client."""
        pass

    @abstractmethod
    async def get_pending(self, limit: int = 100) -> List[Booking]:
        """Get pending bookings."""
        pass

    @abstractmethod
    async def get_failed_retryable(self, max_attempts: int = 5, limit: int = 100) -> List[Booking]:
        """Get failed bookings that can be retried."""
        pass

    @abstractmethod
    async def update(self, booking: Booking) -> Booking:
        """Update existing booking."""
        pass

    @abstractmethod
    async def delete(self, booking_id: int) -> bool:
        """Delete booking."""
        pass


class IAppointmentRepository(ABC):
    """Appointment repository interface."""

    @abstractmethod
    async def create_slot(self, slot: AppointmentSlot) -> AppointmentSlot:
        """Create a new appointment slot."""
        pass

    @abstractmethod
    async def get_available_slots(
        self,
        location: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AppointmentSlot]:
        """Get available appointment slots."""
        pass

    @abstractmethod
    async def reserve_slot(self, slot_id: int) -> bool:
        """Reserve an appointment slot."""
        pass

    @abstractmethod
    async def create_appointment(self, appointment: Appointment) -> Appointment:
        """Create a new appointment."""
        pass

    @abstractmethod
    async def get_appointment_by_reference(self, reference: str) -> Optional[Appointment]:
        """Get appointment by reference."""
        pass

    @abstractmethod
    async def get_appointments_by_client(self, client_id: int) -> List[Appointment]:
        """Get all appointments for a client."""
        pass

    @abstractmethod
    async def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel an appointment."""
        pass
