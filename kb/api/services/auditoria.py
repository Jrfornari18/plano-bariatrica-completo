"""
auditoria.py — Serviço de auditoria e registro de recomendações.

RF-09: Cada resposta gera log com chunks usados, modelo e flag de escalonamento.
RF-10: Feedback persistido e vinculado ao log.
RNF-03: Consentimento LGPD verificado antes de persistir métricas.
RNF-04: Logs estruturados com rastreio de prompt_hash e chunks.
"""
from __future__ import annotations

import logging
import uuid
from typing import Sequence

import asyncpg

from ..services.recuperacao import ChunkRecuperado

logger = logging.getLogger(__name__)


async def obter_ou_criar_perfil(
    pool: asyncpg.Pool,
    pseudonimo: str,
    contexto_slug: str | None = None,
) -> str:
    """
    Obtém ou cria perfil de usuário pelo pseudônimo.
    Retorna o UUID do perfil.

    RNF-02: Sem PII direta — apenas pseudônimo.
    """
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "SELECT id FROM perfil_usuario WHERE pseudonimo = $1", pseudonimo
        )
        if row:
            return str(row["id"])

        # Busca contexto_id se fornecido
        contexto_id = None
        if contexto_slug:
            ctx = await con.fetchrow(
                "SELECT id FROM contexto_clinico WHERE slug = $1", contexto_slug
            )
            contexto_id = ctx["id"] if ctx else None

        novo_id = await con.fetchval(
            """
            INSERT INTO perfil_usuario (pseudonimo, contexto_id, consentimento_lgpd)
            VALUES ($1, $2, TRUE)
            RETURNING id
            """,
            pseudonimo,
            contexto_id,
        )
        logger.info("Novo perfil criado: pseudonimo=%s id=%s", pseudonimo, novo_id)
        return str(novo_id)


async def registrar_metricas(
    pool: asyncpg.Pool,
    perfil_id: str,
    metricas: list[dict],
) -> None:
    """
    Persiste métricas do BodyScan no perfil.
    RNF-03: Consentimento LGPD verificado antes de persistir.
    """
    if not metricas:
        return

    async with pool.acquire() as con:
        # Verifica consentimento
        consentimento = await con.fetchval(
            "SELECT consentimento_lgpd FROM perfil_usuario WHERE id = $1",
            perfil_id,
        )
        if not consentimento:
            logger.warning(
                "Métricas não persistidas: consentimento LGPD ausente para perfil %s",
                perfil_id,
            )
            return

        for m in metricas:
            bio = await con.fetchrow(
                "SELECT id FROM biomarcador WHERE slug = $1", m["biomarcador"]
            )
            if bio:
                await con.execute(
                    """
                    INSERT INTO perfil_metrica (perfil_id, biomarcador_id, valor)
                    VALUES ($1, $2, $3)
                    """,
                    perfil_id,
                    bio["id"],
                    float(m["valor"]),
                )


async def registrar_log(
    pool: asyncpg.Pool,
    perfil_id: str | None,
    recomendacao_id: str | None,
    chunks: Sequence[ChunkRecuperado],
    modelo: str,
    prompt_hash: str,
    houve_escalonamento: bool,
    tipo_alerta: str | None,
) -> str:
    """
    Registra log de recomendação emitida.

    RF-09: Cada resposta gera log com chunks usados, modelo e flag de escalonamento.
    RNF-04: Logs estruturados com rastreio de prompt_hash e chunks.

    Retorna o UUID do log criado.
    """
    chunk_ids = [c.id for c in chunks] if chunks else []

    async with pool.acquire() as con:
        log_id = await con.fetchval(
            """
            INSERT INTO log_recomendacao
                (perfil_id, recomendacao_id, chunks_recuperados,
                 modelo_gerador, prompt_hash,
                 houve_escalonamento, tipo_alerta_disparado)
            VALUES ($1, $2, $3::uuid[], $4, $5, $6, $7::tipo_alerta)
            RETURNING id
            """,
            perfil_id,
            recomendacao_id,
            chunk_ids,
            modelo,
            prompt_hash,
            houve_escalonamento,
            tipo_alerta,
        )

    log_id_str = str(log_id)
    logger.info(
        "Log registrado: id=%s escalonamento=%s chunks=%d modelo=%s hash=%s",
        log_id_str,
        houve_escalonamento,
        len(chunk_ids),
        modelo,
        prompt_hash,
    )
    return log_id_str


async def registrar_feedback(
    pool: asyncpg.Pool,
    log_id: str,
    util: bool | None,
    comentario: str | None,
) -> str:
    """
    Persiste feedback do usuário vinculado ao log.

    RF-10: Feedback persistido e vinculado ao log.
    """
    async with pool.acquire() as con:
        feedback_id = await con.fetchval(
            """
            INSERT INTO feedback_recomendacao (log_id, util, comentario)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            log_id,
            util,
            comentario,
        )

    feedback_id_str = str(feedback_id)
    logger.info("Feedback registrado: id=%s log_id=%s util=%s", feedback_id_str, log_id, util)
    return feedback_id_str


async def buscar_fontes_dos_chunks(
    pool: asyncpg.Pool,
    chunk_ids: list[str],
) -> list[str]:
    """Retorna títulos das fontes associadas aos chunks."""
    if not chunk_ids:
        return []

    async with pool.acquire() as con:
        rows = await con.fetch(
            """
            SELECT DISTINCT f.titulo
            FROM chunk_fonte cf
            JOIN fonte f ON f.id = cf.fonte_id
            WHERE cf.chunk_id = ANY($1::uuid[])
            """,
            chunk_ids,
        )
    return [r["titulo"] for r in rows]
