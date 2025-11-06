"""Client Repository Implementation"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Client
from src.domain.interfaces import IClientRepository
from src.domain.exceptions import ClientNotFoundError, ClientAlreadyExistsError


class ClientRepository(IClientRepository):
    """Client repository implementation with async support."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, client: Client) -> Client:
        """Create a new client."""
        # Check if email already exists
        if await self.exists_by_email(client.email):
            raise ClientAlreadyExistsError(client.email)

        self.session.add(client)
        await self.session.flush()
        await self.session.refresh(client)
        return client

    async def get_by_id(self, client_id: int) -> Optional[Client]:
        """Get client by ID."""
        stmt = select(Client).where(Client.id == client_id, Client.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Client]:
        """Get client by email."""
        stmt = select(Client).where(Client.email == email, Client.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Client]:
        """Get all clients with pagination."""
        stmt = select(Client).where(Client.deleted_at.is_(None))

        if active_only:
            stmt = stmt.where(Client.is_active == True)

        stmt = stmt.offset(skip).limit(limit).order_by(Client.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, client: Client) -> Client:
        """Update existing client."""
        existing = await self.get_by_id(client.id)
        if not existing:
            raise ClientNotFoundError(client_id=client.id)

        client.updated_at = datetime.utcnow()
        await self.session.merge(client)
        await self.session.flush()
        await self.session.refresh(client)
        return client

    async def delete(self, client_id: int, soft: bool = True) -> bool:
        """Delete client (soft or hard delete)."""
        client = await self.get_by_id(client_id)
        if not client:
            raise ClientNotFoundError(client_id=client_id)

        if soft:
            # Soft delete: set deleted_at timestamp
            stmt = (
                update(Client)
                .where(Client.id == client_id)
                .values(deleted_at=datetime.utcnow(), is_active=False)
            )
            await self.session.execute(stmt)
        else:
            # Hard delete: permanently remove
            stmt = delete(Client).where(Client.id == client_id)
            await self.session.execute(stmt)

        await self.session.flush()
        return True

    async def exists_by_email(self, email: str) -> bool:
        """Check if client exists by email."""
        stmt = select(Client.id).where(Client.email == email, Client.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def count_active(self) -> int:
        """Count active clients."""
        from sqlalchemy import func

        stmt = select(func.count(Client.id)).where(
            Client.is_active == True, Client.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def search_by_name(self, name: str, limit: int = 50) -> List[Client]:
        """Search clients by name."""
        search_pattern = f"%{name}%"
        stmt = (
            select(Client)
            .where(
                Client.deleted_at.is_(None),
                (Client.first_name.ilike(search_pattern)) | (Client.last_name.ilike(search_pattern)),
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
