from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from .settings import get_settings


class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass


_engine = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine():
    """Create or return a global async SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_dsn(),
            echo=False,
            pool_pre_ping=True,
            future=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create or return the global async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
            class_=AsyncSession,
        )
    return _session_factory


# PUBLIC_INTERFACE
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession for request-scoped DB interactions."""
    session = get_session_factory()()
    try:
        yield session
        # Let caller decide commit/rollback; most endpoints will commit explicitly.
    finally:
        await session.close()


# PUBLIC_INTERFACE
async def ping_db() -> bool:
    """Check database connectivity with a simple SELECT 1."""
    async with get_session_factory()() as session:
        result = await session.execute(text("SELECT 1"))
        _ = result.scalar_one()
        return True
