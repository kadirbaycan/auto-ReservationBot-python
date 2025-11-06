"""Domain Interfaces - Repository & Service Contracts"""

from .repositories import IClientRepository, IBookingRepository, IAppointmentRepository
from .services import IVFSAutomationService, ICacheService, INotificationService

__all__ = [
    # Repositories
    "IClientRepository",
    "IBookingRepository",
    "IAppointmentRepository",
    # Services
    "IVFSAutomationService",
    "ICacheService",
    "INotificationService",
]
