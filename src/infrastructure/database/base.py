"""Database Base Configuration"""

import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

# Create Base for declarative models
Base = declarative_base()

# Global engine and session instances
_engine: Optional[any] = None
_session_factory: Optional[sessionmaker] = None


def get_database_url() -> str:
    """Get database URL from environment."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/vfs_automation.db")

    # Handle SQLite specific path
    if database_url.startswith("sqlite"):
        # Ensure data directory exists
        os.makedirs("./data", exist_ok=True)

    return database_url


def get_engine(database_url: str = None, echo: bool = False):
    """Get or create database engine."""
    global _engine

    if _engine is None:
        url = database_url or get_database_url()

        # Configure pool based on database type
        if url.startswith("sqlite"):
            # SQLite doesn't support connection pooling well
            engine_args = {
                "connect_args": {"check_same_thread": False},
                "poolclass": NullPool,
            }
        else:
            # PostgreSQL/MySQL with connection pooling
            pool_size = int(os.getenv("DATABASE_POOL_SIZE", "20"))
            max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
            engine_args = {
                "poolclass": QueuePool,
                "pool_size": pool_size,
                "max_overflow": max_overflow,
                "pool_pre_ping": True,  # Verify connections before using
                "pool_recycle": 3600,  # Recycle connections after 1 hour
            }

        _engine = create_engine(url, echo=echo, **engine_args)

    return _engine


def get_session(engine=None):
    """Get or create session factory."""
    global _session_factory

    if _session_factory is None:
        eng = engine or get_engine()
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=eng)

    return _session_factory()


def init_db(engine=None) -> None:
    """Initialize database (create all tables)."""
    eng = engine or get_engine()

    # Import all models to ensure they're registered
    from src.domain.models import Client, Booking, Appointment, AppointmentSlot

    # Create all tables
    Base.metadata.create_all(bind=eng)


def close_db() -> None:
    """Close database connections."""
    global _engine, _session_factory

    if _session_factory:
        _session_factory.close_all()
        _session_factory = None

    if _engine:
        _engine.dispose()
        _engine = None
