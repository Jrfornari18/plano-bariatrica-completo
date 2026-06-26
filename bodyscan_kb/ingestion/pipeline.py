"""
pipeline.py — Pipeline de ingestão e recuperação para BodyScan KB.

Baseado em ingestao_rag.py (referência de arquitetura).
Implementa M2 (ingestão + embeddings) e M3 (recuperação híbrida + regras).

Stack: Python 3.11+, asyncpg, pgvector, OpenAI embeddings.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Sequence

import asyncpg
from pgvector.asyncpg import register_vector

from .embed_provider import EMBED_DIM, embed_fn

# Tipo de função de embedding injetável
EmbedFn = Callable[[Sequence[str]], Awaitable[list[list[float]]]]

# DSN padrão (sobrescrito por variável de ambiente)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bodyscan:bodyscan_secret@localhost:5432/bodyscan_kb",
)

# Pool global (inicializado sob demanda)
_pool: asyncpg.Pool | None = None


# ---------------------------------------------------------------------
# Conexão
# ---------------------------------------------------------------------
async def get_pool() -> asyncpg.Pool:
    """Retorna o pool de conexões, criando-o se necessário."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            init=register_vector,
            min_size=1,
            max_size=8,
        )
    return _pool


async def conectar(dsn: str | None = None) -> asyncpg.Pool:
    """Cria e retorna um pool de conexões."""
    return await asyncpg.create_pool(
        dsn or DATABASE_URL,
        init=register_vector,
        min_size=1,
        max_size=8,
    )


# ---------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------
def dividir_em_chunks(
    texto: str,
    alvo_tokens: int = 350,
    sobreposicao: int = 50,
) -> list[str]:
    """Chunking por sentença com sobreposição.

    Heurística simples (~4 chars/token). Para produção, use tiktoken.
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


# ---------------------------------------------------------------------
# Ingestão: gera embeddings e popula chunk_conhecimento (M2 - RF-03)
# ---------------------------------------------------------------------
async def ingerir_documento(
    pool: asyncpg.Pool,
    documento_id: str,
    embed: EmbedFn | None = None,
) -> int:
    """Ingere um documento, gera embeddings e popula chunk_conhecimento.

    Retorna o número de chunks gerados.
    Raises ValueError se o documento não existir ou a dimensão não bater.
    """
    if embed is None:
        embed = embed_fn

    async with pool.acquire() as con:
        doc = await con.fetchrow(
            """
            SELECT d.id, d.conteudo_md, d.nivel_evidencia,
                   dom.slug AS dominio_slug
            FROM documento_conhecimento d
            LEFT JOIN dominio_conhecimento dom ON dom.id = d.dominio_id
            WHERE d.id = $1
            """,
            documento_id,
        )
        if not doc:
            raise ValueError(f"Documento inexistente: {documento_id}")

        # Busca metadados dos chunks existentes ANTES de deletar
        # para preservar contexto_slugs e requer_supervisao_medica do seed
        existing_meta = await con.fetchrow(
            """
            SELECT contexto_slugs, requer_supervisao_medica
            FROM chunk_conhecimento
            WHERE documento_id = $1
            LIMIT 1
            """,
            documento_id,
        )
        contexto_slugs_orig = existing_meta["contexto_slugs"] if existing_meta else None
        requer_supervisao_orig = existing_meta["requer_supervisao_medica"] if existing_meta else False

        # Remove chunks existentes para re-ingestão idempotente
        await con.execute(
            "DELETE FROM chunk_conhecimento WHERE documento_id = $1",
            documento_id,
        )

        partes = dividir_em_chunks(doc["conteudo_md"])
        if not partes:
            return 0

        vetores = await embed(partes)
        if any(len(v) != EMBED_DIM for v in vetores):
            raise ValueError(
                f"Dimensão do embedding ({len(vetores[0])}) != EMBED_DIM ({EMBED_DIM}). "
                "Ajuste EMBED_DIM e o schema."
            )

        await con.executemany(
            """
            INSERT INTO chunk_conhecimento
                (documento_id, ordem, texto, embedding, tokens,
                 dominio_slug, contexto_slugs, nivel_evidencia, requer_supervisao_medica)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            [
                (
                    documento_id,
                    i,
                    txt,
                    vec,
                    max(1, len(txt) // 4),
                    doc["dominio_slug"],
                    contexto_slugs_orig,
                    doc["nivel_evidencia"],
                    requer_supervisao_orig,
                )
                for i, (txt, vec) in enumerate(zip(partes, vetores), start=1)
            ],
        )
        return len(partes)


async def ingerir_todos_documentos(
    pool: asyncpg.Pool,
    embed: EmbedFn | None = None,
) -> dict[str, int]:
    """Ingere todos os documentos sem embedding ou com embedding nulo.

    Retorna mapa {documento_id: chunks_gerados}.
    """
    if embed is None:
        embed = embed_fn

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
            n = await ingerir_documento(pool, doc_id, embed)
            resultados[doc_id] = n
        except Exception as exc:
            resultados[doc_id] = -1
            print(f"[ERRO] Ingestão do documento {doc_id}: {exc}")

    return resultados


# ---------------------------------------------------------------------
# Governança: detecção de gatilho de escalonamento (M3 - RF-07)
# ---------------------------------------------------------------------
@dataclass
class ResultadoGate:
    """Resultado da avaliação de gatilhos de escalonamento."""
    bloqueado: bool
    tipo_alerta: str | None
    acao: str | None


async def avaliar_gatilhos(
    pool: asyncpg.Pool,
    texto_usuario: str,
) -> ResultadoGate:
    """Avalia o texto do usuário contra os gatilhos de escalonamento.

    Retorna ResultadoGate com bloqueado=True se um gatilho crítico for detectado.
    NUNCA deve ser removido ou contornado.
    """
    alvo = texto_usuario.lower()
    async with pool.acquire() as con:
        gatilhos = await con.fetch(
            "SELECT tipo, acao, palavras_chave FROM gatilho_escalonamento"
        )

    for g in gatilhos:
        for termo in (g["palavras_chave"] or []):
            if termo.lower() in alvo:
                bloqueado = g["acao"] in ("bloquear", "encaminhar_profissional")
                return ResultadoGate(bloqueado, str(g["tipo"]), g["acao"])

    return ResultadoGate(False, None, None)


# ---------------------------------------------------------------------
# Recuperação híbrida com gate de conteúdo servível (M3 - RF-04, RF-08)
# ---------------------------------------------------------------------
@dataclass
class ChunkRecuperado:
    """Chunk recuperado com metadados de distância e supervisão."""
    id: str
    texto: str
    distancia: float
    requer_supervisao: bool
    dominio_slug: str | None = None
    contexto_slugs: list[str] = field(default_factory=list)
    nivel_evidencia: str | None = None


async def recuperar(
    pool: asyncpg.Pool,
    consulta: str,
    embed: EmbedFn | None = None,
    contextos: Sequence[str] | None = None,
    incluir_supervisao: bool = False,
    k: int = 6,
) -> list[ChunkRecuperado]:
    """Busca vetorial filtrada por contexto e pelo gate de governança.

    incluir_supervisao=False respeita a view vw_chunk_servivel:
    conteúdo que exige profissional não é servido a fluxos autônomos.

    RF-04: recuperação híbrida (vetorial + filtro de metadados).
    RF-08: bloqueio de conteúdo requer_supervisao_medica.
    """
    if embed is None:
        embed = embed_fn

    [vetor] = await embed([consulta])

    async with pool.acquire() as con:
        linhas = await con.fetch(
            """
            SELECT id, texto, requer_supervisao_medica,
                   dominio_slug, contexto_slugs, nivel_evidencia,
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
        ChunkRecuperado(
            id=str(r["id"]),
            texto=r["texto"],
            distancia=float(r["distancia"]),
            requer_supervisao=r["requer_supervisao_medica"],
            dominio_slug=r["dominio_slug"],
            contexto_slugs=list(r["contexto_slugs"] or []),
            nivel_evidencia=str(r["nivel_evidencia"]),
        )
        for r in linhas
    ]


async def recuperar_com_trigram(
    pool: asyncpg.Pool,
    consulta: str,
    embed: EmbedFn | None = None,
    contextos: Sequence[str] | None = None,
    incluir_supervisao: bool = False,
    k: int = 6,
    trigram_weight: float = 0.3,
) -> list[ChunkRecuperado]:
    """Recuperação híbrida com reordenação por trigram (pg_trgm).

    Combina distância vetorial com similaridade lexical para termos exatos.
    """
    if embed is None:
        embed = embed_fn

    [vetor] = await embed([consulta])

    async with pool.acquire() as con:
        linhas = await con.fetch(
            """
            SELECT id, texto, requer_supervisao_medica,
                   dominio_slug, contexto_slugs, nivel_evidencia,
                   embedding <=> $1 AS dist_vetorial,
                   1 - similarity(texto, $5) AS dist_trigram
            FROM chunk_conhecimento
            WHERE nivel_evidencia <> 'nao_verificado'
              AND ($2::boolean OR requer_supervisao_medica = FALSE)
              AND ($3::text[] IS NULL OR contexto_slugs && $3::text[])
            ORDER BY (
                (1 - $6::float) * (embedding <=> $1) +
                $6::float * (1 - similarity(texto, $5))
            )
            LIMIT $4
            """,
            vetor,
            incluir_supervisao,
            list(contextos) if contextos else None,
            k,
            consulta,
            trigram_weight,
        )

    return [
        ChunkRecuperado(
            id=str(r["id"]),
            texto=r["texto"],
            distancia=float(r["dist_vetorial"]),
            requer_supervisao=r["requer_supervisao_medica"],
            dominio_slug=r["dominio_slug"],
            contexto_slugs=list(r["contexto_slugs"] or []),
            nivel_evidencia=str(r["nivel_evidencia"]),
        )
        for r in linhas
    ]


# ---------------------------------------------------------------------
# Camada de regras: recomendações elegíveis por contexto (M3 - RF-05)
# ---------------------------------------------------------------------
@dataclass
class RecomendacaoElegivel:
    """Recomendação elegível para um contexto clínico."""
    slug: str
    titulo: str
    forca: str
    requer_supervisao: bool
    condicao_metrica: dict | None = None
    prioridade: int = 100


async def recomendacoes_por_contexto(
    pool: asyncpg.Pool,
    contexto_slug: str,
    metricas: dict[str, float] | None = None,
) -> list[RecomendacaoElegivel]:
    """Retorna recomendações elegíveis para o contexto, filtrando por métricas.

    RF-05: camada de regras seleciona recomendações por contexto + condicao_metrica.
    Ex.: rca > 0.5 em perda_acelerada torna elegível a recomendação de pele.
    """
    async with pool.acquire() as con:
        rows = await con.fetch(
            """
            SELECT r.slug, r.titulo, r.forca, r.requer_supervisao_medica,
                   rr.condicao_metrica, rr.prioridade
            FROM regra_recomendacao rr
            JOIN recomendacao r ON r.id = rr.recomendacao_id AND r.ativo
            JOIN contexto_clinico c ON c.id = rr.contexto_id
            WHERE c.slug = $1 AND rr.ativo
            ORDER BY rr.prioridade
            """,
            contexto_slug,
        )

    resultado: list[RecomendacaoElegivel] = []
    for row in rows:
        cond = row["condicao_metrica"]
        if cond and metricas:
            # Avalia condição declarativa JSONB
            if not _avaliar_condicao(cond, metricas):
                continue

        resultado.append(
            RecomendacaoElegivel(
                slug=row["slug"],
                titulo=row["titulo"],
                forca=str(row["forca"]),
                requer_supervisao=row["requer_supervisao_medica"],
                condicao_metrica=(json.loads(cond) if isinstance(cond, str) else dict(cond)) if cond else None,
                prioridade=row["prioridade"],
            )
        )

    return resultado


def _avaliar_condicao(cond, metricas: dict[str, float]) -> bool:
    """Avalia condição declarativa JSONB contra métricas do usuário.

    Formato suportado:
    {"all": [{"biomarcador": "rca", "op": ">", "valor": 0.5}]}
    {"any": [{"biomarcador": "imc", "op": ">=", "valor": 30}]}

    Aceita tanto dict quanto string JSON (asyncpg pode retornar ambos).
    """
    import json
    if isinstance(cond, str):
        cond = json.loads(cond)
    ops = {
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }

    def avaliar_regra(r: dict) -> bool:
        bio = r.get("biomarcador")
        op = r.get("op", ">")
        valor = r.get("valor")
        if bio not in metricas or valor is None:
            return True  # sem dados, não bloqueia
        return ops.get(op, lambda a, b: True)(metricas[bio], valor)

    if "all" in cond:
        return all(avaliar_regra(r) for r in cond["all"])
    if "any" in cond:
        return any(avaliar_regra(r) for r in cond["any"])

    return True


# ---------------------------------------------------------------------
# Orquestração de alto nível (M4 - RF-06)
# ---------------------------------------------------------------------
async def montar_contexto_para_llm(
    pool: asyncpg.Pool,
    pergunta: str,
    embed: EmbedFn | None = None,
    contexto_clinico: str | None = None,
    metricas: dict[str, float] | None = None,
    incluir_supervisao: bool = False,
) -> dict:
    """Orquestra gate → recuperação → regras para a LLM.

    Retorna material ancorado ou desvio de escalonamento.
    A geração final (chamada à LLM) é responsabilidade do endpoint FastAPI.
    """
    if embed is None:
        embed = embed_fn

    # 1. Gate de escalonamento (human-in-the-loop) — SEMPRE primeiro
    gate = await avaliar_gatilhos(pool, pergunta)
    if gate.bloqueado:
        return {
            "escalonar": True,
            "tipo_alerta": gate.tipo_alerta,
            "acao": gate.acao,
        }

    # 2. Recuperação híbrida com gate de conteúdo servível
    contextos = [contexto_clinico] if contexto_clinico else None
    chunks = await recuperar(
        pool, pergunta, embed,
        contextos=contextos,
        incluir_supervisao=incluir_supervisao,
    )

    # 3. Recomendações elegíveis por contexto + métricas
    recs: list[RecomendacaoElegivel] = []
    if contexto_clinico:
        recs = await recomendacoes_por_contexto(pool, contexto_clinico, metricas)

    return {
        "escalonar": False,
        "chunks": [
            {
                "id": c.id,
                "texto": c.texto,
                "distancia": c.distancia,
                "requer_supervisao": c.requer_supervisao,
                "dominio_slug": c.dominio_slug,
                "contexto_slugs": c.contexto_slugs,
                "nivel_evidencia": c.nivel_evidencia,
            }
            for c in chunks
        ],
        "recomendacoes_elegiveis": [
            {
                "slug": r.slug,
                "titulo": r.titulo,
                "forca": r.forca,
                "requer_supervisao": r.requer_supervisao,
                "prioridade": r.prioridade,
            }
            for r in recs
        ],
        "instrucao_grounding": (
            "Responda APENAS com base nos chunks fornecidos. "
            "Cite as fontes pelo campo 'fonte'. "
            "NÃO prescreva fármacos, doses ou metas calóricas individuais. "
            "Se o tema exigir supervisão médica, oriente buscar profissional. "
            "Se não houver chunks relevantes, recuse e informe que o tema não está coberto."
        ),
    }
