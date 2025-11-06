"""Booking Repository Implementation"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Booking, BookingStatus
from src.domain.interfaces import IBookingRepository
from src.domain.exceptions import BookingNotFoundError


class BookingRepository(IBookingRepository):
    """Booking repository implementation with async support."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, booking: Booking) -> Booking:
        """Create a new booking."""
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID."""
        stmt = select(Booking).where(Booking.id == booking_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_reference(self, reference: str) -> Optional[Booking]:
        """Get booking by reference number."""
        stmt = select(Booking).where(Booking.booking_reference == reference)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_client(self, client_id: int, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings for a client."""
        stmt = (
            select(Booking)
            .where(Booking.client_id == client_id)
            .order_by(Booking.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_pending(self, limit: int = 100) -> List[Booking]:
        """Get pending bookings."""
        stmt = (
            select(Booking)
            .where(Booking.status == BookingStatus.PENDING)
            .order_by(Booking.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_failed_retryable(self, max_attempts: int = 5, limit: int = 100) -> List[Booking]:
        """Get failed bookings that can be retried."""
        now = datetime.utcnow()
        stmt = (
            select(Booking)
            .where(
                Booking.status == BookingStatus.FAILED,
                Booking.attempt_count < max_attempts,
                (Booking.retry_after.is_(None)) | (Booking.retry_after < now),
            )
            .order_by(Booking.last_attempt_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, booking: Booking) -> Booking:
        """Update existing booking."""
        existing = await self.get_by_id(booking.id)
        if not existing:
            raise BookingNotFoundError(booking_id=booking.id)

        booking.updated_at = datetime.utcnow()
        await self.session.merge(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking

    async def delete(self, booking_id: int) -> bool:
        """Delete booking."""
        booking = await self.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError(booking_id=booking_id)

        stmt = delete(Booking).where(Booking.id == booking_id)
        await self.session.execute(stmt)
        await self.session.flush()
        return True

    async def get_by_status(self, status: BookingStatus, limit: int = 100) -> List[Booking]:
        """Get bookings by status."""
        stmt = (
            select(Booking)
            .where(Booking.status == status)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_client(self, client_id: int, status: BookingStatus = None) -> int:
        """Count bookings for a client."""
        from sqlalchemy import func

        stmt = select(func.count(Booking.id)).where(Booking.client_id == client_id)

        if status:
            stmt = stmt.where(Booking.status == status)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_recent(self, hours: int = 24, limit: int = 100) -> List[Booking]:
        """Get recent bookings within specified hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Booking)
            .where(Booking.created_at >= cutoff)
            .order_by(Booking.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


from datetime import timedelta
