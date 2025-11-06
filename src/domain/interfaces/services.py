"""Service Interfaces - Business Logic Contracts"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List
from datetime import datetime


class IVFSAutomationService(ABC):
    """VFS automation service interface."""

    @abstractmethod
    async def check_availability(self, url: str) -> dict:
        """Check appointment availability."""
        pass

    @abstractmethod
    async def book_appointment(self, client_id: int) -> dict:
        """Book appointment for client."""
        pass

    @abstractmethod
    async def monitor_slots(self, duration_minutes: int) -> None:
        """Monitor slots for specified duration."""
        pass


class ICacheService(ABC):
    """Cache service interface."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    async def clear(self, pattern: str = None) -> int:
        """Clear cache (optionally by pattern)."""
        pass


class INotificationService(ABC):
    """Notification service interface."""

    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email notification."""
        pass

    @abstractmethod
    async def send_telegram(self, chat_id: str, message: str) -> bool:
        """Send Telegram notification."""
        pass

    @abstractmethod
    async def notify_booking_success(self, client_email: str, booking_reference: str) -> bool:
        """Notify booking success."""
        pass

    @abstractmethod
    async def notify_booking_failure(self, client_email: str, error_message: str) -> bool:
        """Notify booking failure."""
        pass
