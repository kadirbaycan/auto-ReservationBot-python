"""Appointment Domain Model"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Integer, Boolean, Text
from src.infrastructure.database.base import Base


class AppointmentSlot(Base):
    """Appointment slot entity representing available time slots."""

    __tablename__ = "appointment_slots"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Slot Information
    slot_date = Column(DateTime, nullable=False, index=True)
    slot_time = Column(String(10), nullable=True)  # HH:MM format
    location = Column(String(255), nullable=False)
    location_code = Column(String(50), nullable=True, index=True)

    # Availability
    is_available = Column(Boolean, default=True, index=True)
    total_capacity = Column(Integer, default=1)
    remaining_capacity = Column(Integer, default=1)

    # Metadata
    source_url = Column(String(500), nullable=True)
    external_id = Column(String(100), nullable=True, index=True)
    metadata_json = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True, index=True)

    def __repr__(self) -> str:
        return f"<AppointmentSlot(id={self.id}, date={self.slot_date}, location='{self.location}', available={self.is_available})>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "slot_date": self.slot_date.isoformat() if self.slot_date else None,
            "slot_time": self.slot_time,
            "location": self.location,
            "is_available": self.is_available,
            "remaining_capacity": self.remaining_capacity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @property
    def is_expired(self) -> bool:
        """Check if slot has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    def reserve(self) -> bool:
        """Reserve a slot if available."""
        if not self.is_available or self.remaining_capacity <= 0:
            return False
        self.remaining_capacity -= 1
        if self.remaining_capacity == 0:
            self.is_available = False
        return True


class Appointment(Base):
    """Appointment entity representing booked appointments."""

    __tablename__ = "appointments"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Keys
    client_id = Column(Integer, nullable=False, index=True)
    booking_id = Column(Integer, nullable=True, index=True)
    slot_id = Column(Integer, nullable=True)

    # Appointment Details
    appointment_reference = Column(String(100), unique=True, nullable=False, index=True)
    appointment_date = Column(DateTime, nullable=False, index=True)
    appointment_time = Column(String(10), nullable=True)
    location = Column(String(255), nullable=False)

    # Status
    is_confirmed = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)

    # Contact
    confirmation_email_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, ref='{self.appointment_reference}', date={self.appointment_date})>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "appointment_reference": self.appointment_reference,
            "appointment_date": self.appointment_date.isoformat() if self.appointment_date else None,
            "appointment_time": self.appointment_time,
            "location": self.location,
            "is_confirmed": self.is_confirmed,
            "is_cancelled": self.is_cancelled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
