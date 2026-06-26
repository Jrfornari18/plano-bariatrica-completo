"""
Engine assíncrono e factory de sessão.
Suporta SQLite (aiosqlite) para MVP e PostgreSQL (asyncpg) para produção.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    # SQLite: evita erros de thread em async
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.database_url
    else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    """Base declarativa compartilhada por todos os modelos ORM."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection do FastAPI para sessão de banco."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_all_tables() -> None:
    """Cria todas as tabelas (usado em testes e desenvolvimento)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all_tables() -> None:
    """Remove todas as tabelas (usado em testes)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
