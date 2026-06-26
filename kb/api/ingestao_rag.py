"""
ingestao_rag.py — Referência de ingestão e recuperação para a BodyScan KB.

Stack-alvo: Python 3.11+, FastAPI, PostgreSQL + pgvector via asyncpg.
Dependências: asyncpg, pgvector, e um provedor de embeddings (pluggável).

Este módulo é uma REFERÊNCIA de arquitetura, não um produto final. Os pontos
de governança clínica (gate de supervisão, escalonamento) são intencionais e
NÃO devem ser removidos para "simplificar".

    pip install asyncpg pgvector
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Awaitable, Callable, Sequence

import asyncpg
from pgvector.asyncpg import register_vector

# Dimensão do embedding — DEVE bater com schema.sql (NOTA 1).
EMBED_DIM = 1536

# Função de embedding injetada (OpenAI, modelo local, etc.).
# Recebe textos, devolve um vetor por texto.
EmbedFn = Callable[[Sequence[str]], Awaitable[list[list[float]]]]


# ---------------------------------------------------------------------
# Conexão
# ---------------------------------------------------------------------
async def conectar(dsn: str) -> asyncpg.Pool:
    pool = await asyncpg.create_pool(dsn, init=register_vector, min_size=1, max_size=8)
    return pool


# ---------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------
def dividir_em_chunks(texto: str, alvo_tokens: int = 350, sobreposicao: int = 50) -> list[str]:
    """Chunking simples por sentença com sobreposição. Substitua por um
    splitter consciente de tokens (tiktoken) em produção."""
    sentencas = re.split(r"(?<=[.!?])\s+", texto.strip())
    chunks, atual, contagem = [], [], 0
    for s in sentencas:
        aprox = max(1, len(s) // 4)  # heurística ~4 chars/token
        if contagem + aprox > alvo_tokens and atual:
            chunks.append(" ".join(atual))
            # sobreposição: mantém as últimas sentenças
            atual = atual[-1:] if sobreposicao else []
            contagem = sum(max(1, len(x) // 4) for x in atual)
        atual.append(s)
        contagem += aprox
    if atual:
        chunks.append(" ".join(atual))
    return chunks


# ---------------------------------------------------------------------
# Ingestão: gera embeddings e popula chunk_conhecimento
# ---------------------------------------------------------------------
async def ingerir_documento(
    pool: asyncpg.Pool,
    documento_id: str,
    embed: EmbedFn,
) -> int:
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
            raise ValueError("documento inexistente")

        partes = dividir_em_chunks(doc["conteudo_md"])
        vetores = await embed(partes)
        if any(len(v) != EMBED_DIM for v in vetores):
            raise ValueError(f"embedding != {EMBED_DIM}: ajuste EMBED_DIM e o schema")

        await con.executemany(
            """
            INSERT INTO chunk_conhecimento
                (documento_id, ordem, texto, embedding, tokens,
                 dominio_slug, nivel_evidencia)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            [
                (documento_id, i, txt, vec, max(1, len(txt) // 4),
                 doc["dominio_slug"], doc["nivel_evidencia"])
                for i, (txt, vec) in enumerate(zip(partes, vetores), start=1)
            ],
        )
        return len(partes)


# ---------------------------------------------------------------------
# Governança: detecção de gatilho de escalonamento (human-in-the-loop)
# ---------------------------------------------------------------------
@dataclass
class ResultadoGate:
    bloqueado: bool
    tipo_alerta: str | None
    acao: str | None


async def avaliar_gatilhos(pool: asyncpg.Pool, texto_usuario: str) -> ResultadoGate:
    alvo = texto_usuario.lower()
    async with pool.acquire() as con:
        gatilhos = await con.fetch(
            "SELECT tipo, acao, palavras_chave FROM gatilho_escalonamento"
        )
    for g in gatilhos:
        for termo in (g["palavras_chave"] or []):
            if termo.lower() in alvo:
                bloqueado = g["acao"] in ("bloquear", "encaminhar_profissional")
                return ResultadoGate(bloqueado, g["tipo"], g["acao"])
    return ResultadoGate(False, None, None)


# ---------------------------------------------------------------------
# Recuperação híbrida com gate de conteúdo servível
# ---------------------------------------------------------------------
@dataclass
class ChunkRecuperado:
    id: str
    texto: str
    distancia: float
    requer_supervisao: bool


async def recuperar(
    pool: asyncpg.Pool,
    consulta: str,
    embed: EmbedFn,
    contextos: Sequence[str] | None = None,
    incluir_supervisao: bool = False,
    k: int = 6,
) -> list[ChunkRecuperado]:
    """Busca vetorial filtrada por contexto e pelo gate de governança.

    incluir_supervisao=False respeita a view vw_chunk_servivel: conteúdo que
    exige profissional não é servido a fluxos autônomos.
    """
    [vetor] = await embed([consulta])
    async with pool.acquire() as con:
        linhas = await con.fetch(
            """
            SELECT id, texto, requer_supervisao_medica,
                   embedding <=> $1 AS distancia
            FROM chunk_conhecimento
            WHERE nivel_evidencia <> 'nao_verificado'
              AND ($2::boolean OR requer_supervisao_medica = FALSE)
              AND ($3::text[] IS NULL OR contexto_slugs && $3::text[])
            ORDER BY embedding <=> $1
            LIMIT $4
            """,
            vetor,
            incluir_supervisao,
            list(contextos) if contextos else None,
            k,
        )
    return [
        ChunkRecuperado(str(r["id"]), r["texto"], float(r["distancia"]),
                        r["requer_supervisao_medica"])
        for r in linhas
    ]


# ---------------------------------------------------------------------
# Recomendações elegíveis por contexto (camada de regras)
# ---------------------------------------------------------------------
async def recomendacoes_por_contexto(
    pool: asyncpg.Pool, contexto_slug: str
) -> list[asyncpg.Record]:
    async with pool.acquire() as con:
        return await con.fetch(
            """
            SELECT r.slug, r.titulo, r.forca, r.requer_supervisao_medica
            FROM regra_recomendacao rr
            JOIN recomendacao r ON r.id = rr.recomendacao_id AND r.ativo
            JOIN contexto_clinico c ON c.id = rr.contexto_id
            WHERE c.slug = $1 AND rr.ativo
            ORDER BY rr.prioridade
            """,
            contexto_slug,
        )


# ---------------------------------------------------------------------
# Orquestração de alto nível (exemplo de uso no endpoint FastAPI)
# ---------------------------------------------------------------------
async def montar_contexto_para_llm(
    pool: asyncpg.Pool,
    pergunta: str,
    embed: EmbedFn,
    contexto_clinico: str | None = None,
) -> dict:
    """Retorna o material ancorado para a LLM ou um desvio de escalonamento.
    A geração final (chamada à LLM) é responsabilidade da camada de aplicação,
    que deve restringir a resposta aos chunks aqui retornados e citar as fontes."""
    gate = await avaliar_gatilhos(pool, pergunta)
    if gate.bloqueado:
        return {"escalonar": True, "tipo_alerta": gate.tipo_alerta, "acao": gate.acao}

    contextos = [contexto_clinico] if contexto_clinico else None
    chunks = await recuperar(pool, pergunta, embed, contextos=contextos)
    recs = (
        await recomendacoes_por_contexto(pool, contexto_clinico)
        if contexto_clinico else []
    )
    return {
        "escalonar": False,
        "chunks": [c.__dict__ for c in chunks],
        "recomendacoes_elegiveis": [dict(r) for r in recs],
        "instrucao_grounding": (
            "Responda apenas com base nos chunks fornecidos. Cite as fontes. "
            "Não prescreva fármacos, doses ou metas calóricas individuais. "
            "Recuse e oriente buscar profissional quando o tema exigir supervisão."
        ),
    }
