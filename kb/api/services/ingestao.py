"""
ingestao.py — Pipeline de ingestão: chunking + embeddings + persistência.

Baseado em ingestao_rag.py (referência de arquitetura).
Implementa EmbedFn com OpenAI text-embedding-3-small.
"""
from __future__ import annotations

import re
import logging
from typing import Sequence

import asyncpg

from ..config import get_settings
from .embeddings import embed as openai_embed

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Chunking por sentença com sobreposição
# -------------------------------------------------------------------------
def dividir_em_chunks(
    texto: str,
    alvo_tokens: int = 350,
    sobreposicao: int = 50,
) -> list[str]:
    """
    Chunking simples por sentença com sobreposição.
    Heurística ~4 chars/token (substituir por tiktoken em produção).
    """
    sentencas = re.split(r"(?<=[.!?])\s+", texto.strip())
    chunks: list[str] = []
    atual: list[str] = []
    contagem = 0

    for s in sentencas:
        aprox = max(1, len(s) // 4)
        if contagem + aprox > alvo_tokens and atual:
            chunks.append(" ".join(atual))
            atual = atual[-1:] if sobreposicao else []
            contagem = sum(max(1, len(x) // 4) for x in atual)
        atual.append(s)
        contagem += aprox

    if atual:
        chunks.append(" ".join(atual))

    return chunks


# -------------------------------------------------------------------------
# Ingestão de documento: gera embeddings e popula chunk_conhecimento
# -------------------------------------------------------------------------
async def ingerir_documento(
    pool: asyncpg.Pool,
    documento_id: str,
) -> int:
    """
    Lê documento_conhecimento, divide em chunks, gera embeddings via OpenAI
    e persiste em chunk_conhecimento.

    Retorna o número de chunks gerados.
    Lança ValueError se o documento não existir ou a dimensão for incoerente.
    """
    settings = get_settings()

    async with pool.acquire() as con:
        doc = await con.fetchrow(
            """
            SELECT d.conteudo_md, d.nivel_evidencia, dom.slug AS dominio_slug
            FROM documento_conhecimento d
            LEFT JOIN dominio_conhecimento dom ON dom.id = d.dominio_id
            WHERE d.id = $1
            """,
            documento_id,
        )
        if not doc:
            raise ValueError(f"documento_conhecimento não encontrado: {documento_id}")

        partes = dividir_em_chunks(doc["conteudo_md"])
        logger.info(
            "Ingerindo documento %s: %d chunks gerados", documento_id, len(partes)
        )

        vetores = await openai_embed(partes)

        # Valida dimensão
        for v in vetores:
            if len(v) != settings.embed_dim:
                raise ValueError(
                    f"Embedding dim={len(v)} != EMBED_DIM={settings.embed_dim}"
                )

        # Remove chunks anteriores do documento (idempotente)
        await con.execute(
            "DELETE FROM chunk_conhecimento WHERE documento_id = $1", documento_id
        )

        # Recupera metadados do chunk original (contexto_slugs, requer_supervisao)
        chunk_meta = await con.fetchrow(
            """
            SELECT contexto_slugs, requer_supervisao_medica
            FROM chunk_conhecimento
            WHERE documento_id = $1
            ORDER BY ordem
            LIMIT 1
            """,
            documento_id,
        )
        contexto_slugs = list(chunk_meta["contexto_slugs"]) if chunk_meta and chunk_meta["contexto_slugs"] else []
        requer_supervisao = chunk_meta["requer_supervisao_medica"] if chunk_meta else False

        await con.executemany(
            """
            INSERT INTO chunk_conhecimento
                (documento_id, ordem, texto, embedding, tokens,
                 dominio_slug, nivel_evidencia, contexto_slugs, requer_supervisao_medica)
            VALUES ($1, $2, $3, $4::vector, $5, $6, $7, $8, $9)
            """,
            [
                (
                    documento_id,
                    i,
                    txt,
                    vetores[i - 1],
                    max(1, len(txt) // 4),
                    doc["dominio_slug"],
                    doc["nivel_evidencia"],
                    contexto_slugs,
                    requer_supervisao,
                )
                for i, txt in enumerate(partes, start=1)
            ],
        )

        logger.info(
            "Documento %s: %d chunks persistidos com embedding dim=%d",
            documento_id,
            len(partes),
            settings.embed_dim,
        )
        return len(partes)


# -------------------------------------------------------------------------
# Ingestão em lote: processa todos os documentos sem embedding
# -------------------------------------------------------------------------
async def ingerir_todos_documentos(pool: asyncpg.Pool) -> dict[str, int]:
    """
    Ingere todos os documentos que ainda não têm chunks com embedding.
    Retorna mapa {documento_id: chunks_gerados}.
    """
    async with pool.acquire() as con:
        docs = await con.fetch(
            """
            SELECT DISTINCT d.id::text
            FROM documento_conhecimento d
            WHERE NOT EXISTS (
                SELECT 1 FROM chunk_conhecimento c
                WHERE c.documento_id = d.id
                  AND c.embedding IS NOT NULL
                  AND c.nivel_evidencia <> 'nao_verificado'
            )
            """
        )

    resultados: dict[str, int] = {}
    for row in docs:
        doc_id = row["id"]
        try:
            n = await ingerir_documento(pool, doc_id)
            resultados[doc_id] = n
        except Exception as exc:
            logger.error("Erro ao ingerir documento %s: %s", doc_id, exc)
            resultados[doc_id] = -1

    return resultados
