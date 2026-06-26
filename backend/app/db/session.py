"""
Gerenciamento de conexão com SQLite via aiosqlite (RNF-06).
"""
import aiosqlite
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_db_path: str = settings.database_path


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Context manager que fornece uma conexão aiosqlite."""
    async with aiosqlite.connect(_db_path) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        except Exception:
            await conn.rollback()
            raise
        else:
            await conn.commit()


async def check_db_connection() -> bool:
    """Verifica se o banco está acessível (usado no healthcheck)."""
    try:
        async with get_db() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as exc:
        logger.error("Falha na conexão com o banco: %s", exc)
        return False
