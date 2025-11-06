"""Unit tests for Client Repository"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.domain.models import Client
from src.domain.exceptions import ClientNotFoundError, ClientAlreadyExistsError
from src.infrastructure.repositories import ClientRepository
from src.infrastructure.database import Base


@pytest.fixture
async def db_session():
    """Create test database session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def sample_client():
    """Create sample client data."""
    return Client(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        password_hash="hashed_password",
        mobile_country_code="+1",
        mobile_number="1234567890",
        date_of_birth="1990-01-01",
        gender="male",
        current_nationality="US",
        passport_number="AB123456",
        visa_type="tourist",
    )


@pytest.mark.asyncio
class TestClientRepository:
    """Test client repository operations."""

    async def test_create_client(self, db_session, sample_client):
        """Test creating a new client."""
        repo = ClientRepository(db_session)

        created_client = await repo.create(sample_client)

        assert created_client.id is not None
        assert created_client.email == "john.doe@example.com"
        assert created_client.first_name == "John"

    async def test_create_duplicate_email(self, db_session, sample_client):
        """Test creating client with duplicate email."""
        repo = ClientRepository(db_session)

        # Create first client
        await repo.create(sample_client)
        await db_session.commit()

        # Try to create duplicate
        duplicate = Client(
            first_name="Jane",
            last_name="Doe",
            email="john.doe@example.com",  # Same email
            password_hash="different_hash",
            mobile_country_code="+1",
            mobile_number="9876543210",
            date_of_birth="1995-01-01",
        )

        with pytest.raises(ClientAlreadyExistsError):
            await repo.create(duplicate)

    async def test_get_by_id(self, db_session, sample_client):
        """Test getting client by ID."""
        repo = ClientRepository(db_session)

        created = await repo.create(sample_client)
        await db_session.commit()

        found = await repo.get_by_id(created.id)

        assert found is not None
        assert found.id == created.id
        assert found.email == created.email

    async def test_get_by_email(self, db_session, sample_client):
        """Test getting client by email."""
        repo = ClientRepository(db_session)

        await repo.create(sample_client)
        await db_session.commit()

        found = await repo.get_by_email("john.doe@example.com")

        assert found is not None
        assert found.email == "john.doe@example.com"

    async def test_get_all_clients(self, db_session):
        """Test getting all clients with pagination."""
        repo = ClientRepository(db_session)

        # Create multiple clients
        for i in range(5):
            client = Client(
                first_name=f"Client{i}",
                last_name="Test",
                email=f"client{i}@example.com",
                password_hash="hash",
                mobile_country_code="+1",
                mobile_number=f"12345678{i}",
                date_of_birth="1990-01-01",
            )
            await repo.create(client)

        await db_session.commit()

        # Get all clients
        clients = await repo.get_all(skip=0, limit=10)

        assert len(clients) == 5

    async def test_update_client(self, db_session, sample_client):
        """Test updating client."""
        repo = ClientRepository(db_session)

        created = await repo.create(sample_client)
        await db_session.commit()

        # Update
        created.first_name = "Jane"
        created.mobile_number = "9999999999"

        updated = await repo.update(created)
        await db_session.commit()

        assert updated.first_name == "Jane"
        assert updated.mobile_number == "9999999999"

    async def test_soft_delete_client(self, db_session, sample_client):
        """Test soft deleting client."""
        repo = ClientRepository(db_session)

        created = await repo.create(sample_client)
        await db_session.commit()

        # Soft delete
        result = await repo.delete(created.id, soft=True)
        await db_session.commit()

        assert result is True

        # Client should not be found
        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_exists_by_email(self, db_session, sample_client):
        """Test checking if client exists by email."""
        repo = ClientRepository(db_session)

        exists_before = await repo.exists_by_email("john.doe@example.com")
        assert exists_before is False

        await repo.create(sample_client)
        await db_session.commit()

        exists_after = await repo.exists_by_email("john.doe@example.com")
        assert exists_after is True

    async def test_count_active_clients(self, db_session):
        """Test counting active clients."""
        repo = ClientRepository(db_session)

        # Create clients
        for i in range(3):
            client = Client(
                first_name=f"Client{i}",
                last_name="Test",
                email=f"client{i}@example.com",
                password_hash="hash",
                mobile_country_code="+1",
                mobile_number=f"12345678{i}",
                date_of_birth="1990-01-01",
                is_active=True,
            )
            await repo.create(client)

        await db_session.commit()

        count = await repo.count_active()
        assert count == 3

    async def test_search_by_name(self, db_session):
        """Test searching clients by name."""
        repo = ClientRepository(db_session)

        # Create clients
        clients_data = [
            ("John", "Doe"),
            ("Jane", "Smith"),
            ("Johnny", "Appleseed"),
        ]

        for first, last in clients_data:
            client = Client(
                first_name=first,
                last_name=last,
                email=f"{first.lower()}@example.com",
                password_hash="hash",
                mobile_country_code="+1",
                mobile_number="1234567890",
                date_of_birth="1990-01-01",
            )
            await repo.create(client)

        await db_session.commit()

        # Search for "John"
        results = await repo.search_by_name("John")
        assert len(results) == 2  # John and Johnny
