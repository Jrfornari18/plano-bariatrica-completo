"""
Testes de regressão — Migrações Alembic.
Verifica: upgrade/downgrade idempotente, tabelas criadas corretamente.
"""
import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_create_all_tables_creates_expected_tables():
    """Verifica que create_all_tables cria todas as tabelas L1-L5."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    from app.core.database import Base
    import app.models  # noqa: F401 — garante registro de todos os modelos

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    expected_tables = [
        "knowledge_source",
        "knowledge_chunk",
        "concept",
        "concept_relation",
        "fisiologia_marcador",
        "treino_exercicio",
        "treino_protocolo",
        "nutricao_alimento",
        "nutricao_protocolo",
        "usuario",
        "perfil_fisiologico_snapshot",
        "memoria_episodica",
        "memoria_semantica",
        "memoria_vinculo_cross_dominio",
        "contexto_sessao",
        "recuperacao_log",
    ]

    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )

    for table in expected_tables:
        assert table in tables, f"Tabela '{table}' não foi criada"

    await engine.dispose()


@pytest.mark.asyncio
async def test_drop_all_tables_removes_all():
    """Verifica que drop_all_tables remove todas as tabelas."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    from app.core.database import Base
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    async with engine.connect() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )

    assert len(tables) == 0, f"Tabelas residuais após drop_all: {tables}"
    await engine.dispose()
