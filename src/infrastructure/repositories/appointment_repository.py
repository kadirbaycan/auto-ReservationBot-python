"""Appointment Repository Implementation"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Appointment, AppointmentSlot
from src.domain.interfaces import IAppointmentRepository
from src.domain.exceptions import AppointmentNotFoundError, NoSlotsAvailableError


class AppointmentRepository(IAppointmentRepository):
    """Appointment repository implementation with async support."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_slot(self, slot: AppointmentSlot) -> AppointmentSlot:
        """Create a new appointment slot."""
        self.session.add(slot)
        await self.session.flush()
        await self.session.refresh(slot)
        return slot

    async def get_available_slots(
        self,
        location: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AppointmentSlot]:
        """Get available appointment slots."""
        stmt = select(AppointmentSlot).where(
            AppointmentSlot.is_available == True,
            AppointmentSlot.remaining_capacity > 0,
        )

        if location:
            stmt = stmt.where(AppointmentSlot.location == location)

        if from_date:
            stmt = stmt.where(AppointmentSlot.slot_date >= from_date)

        if to_date:
            stmt = stmt.where(AppointmentSlot.slot_date <= to_date)

        # Filter out expired slots
        now = datetime.utcnow()
        stmt = stmt.where(
            (AppointmentSlot.expires_at.is_(None)) | (AppointmentSlot.expires_at > now)
        )

        stmt = stmt.order_by(AppointmentSlot.slot_date.asc()).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def reserve_slot(self, slot_id: int) -> bool:
        """Reserve an appointment slot."""
        slot = await self.session.get(AppointmentSlot, slot_id)

        if not slot:
            raise NoSlotsAvailableError()

        if not slot.is_available or slot.remaining_capacity <= 0:
            return False

        if slot.is_expired:
            return False

        # Reserve the slot
        slot.remaining_capacity -= 1
        if slot.remaining_capacity == 0:
            slot.is_available = False

        await self.session.flush()
        return True

    async def create_appointment(self, appointment: Appointment) -> Appointment:
        """Create a new appointment."""
        self.session.add(appointment)
        await self.session.flush()
        await self.session.refresh(appointment)
        return appointment

    async def get_appointment_by_reference(self, reference: str) -> Optional[Appointment]:
        """Get appointment by reference."""
        stmt = select(Appointment).where(Appointment.appointment_reference == reference)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_appointments_by_client(self, client_id: int) -> List[Appointment]:
        """Get all appointments for a client."""
        stmt = (
            select(Appointment)
            .where(Appointment.client_id == client_id)
            .order_by(Appointment.appointment_date.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel an appointment."""
        appointment = await self.session.get(Appointment, appointment_id)

        if not appointment:
            raise AppointmentNotFoundError(appointment_id=appointment_id)

        appointment.is_cancelled = True
        appointment.cancelled_at = datetime.utcnow()

        await self.session.flush()
        return True

    async def get_upcoming_appointments(self, days: int = 30, limit: int = 100) -> List[Appointment]:
        """Get upcoming appointments."""
        from datetime import timedelta

        now = datetime.utcnow()
        future = now + timedelta(days=days)

        stmt = (
            select(Appointment)
            .where(
                Appointment.appointment_date >= now,
                Appointment.appointment_date <= future,
                Appointment.is_cancelled == False,
            )
            .order_by(Appointment.appointment_date.asc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
