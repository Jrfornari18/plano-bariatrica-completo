"""
database.py — Pool de conexão asyncpg com suporte a pgvector.
"""
from __future__ import annotations

import asyncpg
from pgvector.asyncpg import register_vector

from .config import get_settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    """Retorna o pool global, criando-o na primeira chamada."""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = await asyncpg.create_pool(
            settings.database_url,
            init=register_vector,
            min_size=1,
            max_size=10,
        )
    return _pool


async def close_pool() -> None:
    """Fecha o pool ao encerrar a aplicação."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
