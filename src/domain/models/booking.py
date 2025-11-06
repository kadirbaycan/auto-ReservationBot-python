"""Booking Domain Model"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship

from src.infrastructure.database.base import Base


class BookingStatus(str, Enum):
    """Booking status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Booking(Base):
    """Booking entity representing a visa appointment booking."""

    __tablename__ = "bookings"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Booking Information
    booking_reference = Column(String(100), unique=True, nullable=True, index=True)
    appointment_date = Column(DateTime, nullable=True)
    appointment_location = Column(String(255), nullable=True)

    # Status
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)

    # Attempt Information
    attempt_count = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)

    # Error Tracking
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    retry_after = Column(DateTime, nullable=True)

    # Metadata
    browser_session_id = Column(String(100), nullable=True)
    user_agent = Column(String(500), nullable=True)
    proxy_used = Column(String(100), nullable=True)

    # Additional Data (JSON)
    metadata_json = Column(Text, nullable=True)  # Store as JSON string

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="bookings")

    def __repr__(self) -> str:
        return f"<Booking(id={self.id}, client_id={self.client_id}, status='{self.status.value}', ref='{self.booking_reference}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "booking_reference": self.booking_reference,
            "appointment_date": self.appointment_date.isoformat() if self.appointment_date else None,
            "appointment_location": self.appointment_location,
            "status": self.status.value,
            "attempt_count": self.attempt_count,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def mark_completed(self, booking_reference: str, appointment_date: Optional[datetime] = None) -> None:
        """Mark booking as completed."""
        self.status = BookingStatus.COMPLETED
        self.booking_reference = booking_reference
        self.appointment_date = appointment_date
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_message: str, error_code: Optional[str] = None) -> None:
        """Mark booking as failed."""
        self.status = BookingStatus.FAILED
        self.error_message = error_message
        self.error_code = error_code
        self.last_attempt_at = datetime.utcnow()
        self.attempt_count += 1

    def can_retry(self, max_attempts: int = 5) -> bool:
        """Check if booking can be retried."""
        if self.status == BookingStatus.COMPLETED:
            return False
        if self.attempt_count >= max_attempts:
            return False
        if self.retry_after and datetime.utcnow() < self.retry_after:
            return False
        return True
