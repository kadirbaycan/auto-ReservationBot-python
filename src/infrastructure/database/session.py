"""Async Database Session Management"""

import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool


# Global async engine
_async_engine = None
async_session_maker = None


def get_async_database_url() -> str:
    """Get async database URL from environment."""
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/vfs_automation.db")

    # Convert postgresql to postgresql+asyncpg if needed
    if database_url.startswith("postgresql://") and "asyncpg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    return database_url


def get_async_engine(database_url: str = None, echo: bool = False):
    """Get or create async database engine."""
    global _async_engine

    if _async_engine is None:
        url = database_url or get_async_database_url()

        # Configure pool based on database type
        if "sqlite" in url:
            # SQLite doesn't support connection pooling well
            engine_args = {
                "connect_args": {"check_same_thread": False},
                "poolclass": NullPool,
            }
        else:
            # PostgreSQL/MySQL with async connection pooling
            pool_size = int(os.getenv("DATABASE_POOL_SIZE", "20"))
            max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
            engine_args = {
                "poolclass": AsyncAdaptedQueuePool,
                "pool_size": pool_size,
                "max_overflow": max_overflow,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
            }

        _async_engine = create_async_engine(url, echo=echo, **engine_args)

    return _async_engine


def init_async_session_maker() -> None:
    """Initialize async session maker."""
    global async_session_maker

    if async_session_maker is None:
        engine = get_async_engine()
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session.

    Usage:
        async with get_async_session() as session:
            # Use session here
            pass
    """
    if async_session_maker is None:
        init_async_session_maker()

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_async_db() -> None:
    """Close async database connections."""
    global _async_engine, async_session_maker

    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None

    async_session_maker = None
