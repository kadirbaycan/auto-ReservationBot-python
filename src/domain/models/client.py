"""Client Domain Model"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship

from src.infrastructure.database.base import Base


class Client(Base):
    """Client entity representing a visa applicant."""

    __tablename__ = "clients"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Personal Information
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Contact Information
    mobile_country_code = Column(String(10), nullable=False)
    mobile_number = Column(String(20), nullable=False)

    # Identity Information
    date_of_birth = Column(String(10), nullable=False)  # YYYY-MM-DD
    gender = Column(String(10))
    current_nationality = Column(String(100))
    passport_number = Column(String(50), index=True)
    passport_expiry = Column(String(10))  # YYYY-MM-DD

    # Application Details
    visa_type = Column(String(100))
    application_center = Column(String(100))
    service_center = Column(String(100))
    trip_reason = Column(String(255))

    # Status & Metadata
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    last_booking_attempt = Column(DateTime, nullable=True)
    successful_bookings = Column(Integer, default=0)
    failed_bookings = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    bookings = relationship("Booking", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Client(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"

    def to_dict(self) -> dict:
        """Convert to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "mobile_country_code": self.mobile_country_code,
            "mobile_number": self.mobile_number,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "current_nationality": self.current_nationality,
            "passport_number": self.passport_number,
            "visa_type": self.visa_type,
            "is_active": self.is_active,
            "successful_bookings": self.successful_bookings,
            "failed_bookings": self.failed_bookings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def full_name(self) -> str:
        """Get full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_deleted(self) -> bool:
        """Check if soft deleted."""
        return self.deleted_at is not None
