"""
recuperacao.py — Recuperação híbrida e camada de regras.

Implementa:
  - recuperar(): busca vetorial + filtro de metadados + gate de supervisão
  - recuperar_com_trigram(): reordenação opcional por trigram (pg_trgm)
  - recomendacoes_por_contexto(): seleção de recomendações elegíveis por contexto
  - avaliar_condicao_metrica(): avalia regras declarativas em JSONB
  - avaliar_gatilhos(): gate de escalonamento (human-in-the-loop)

Governança clínica:
  - Gate vw_chunk_servivel: exclui conteúdo nao_verificado ou requer_supervisao
  - Gate gatilho_escalonamento: detecta sinais de risco e bloqueia recomendação autônoma
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Sequence

import asyncpg

from .embeddings import embed as embed_fn

logger = logging.getLogger(__name__)


# -------------------------------------------------------------------------
# Tipos de dados
# -------------------------------------------------------------------------

@dataclass
class ChunkRecuperado:
    id: str
    texto: str
    distancia: float
    requer_supervisao: bool
    dominio_slug: str | None = None
    contexto_slugs: list[str] = field(default_factory=list)
    nivel_evidencia: str = "fisiologia_estabelecida"


@dataclass
class ResultadoGate:
    bloqueado: bool
    tipo_alerta: str | None
    acao: str | None


@dataclass
class RecomendacaoElegivel:
    id: str
    slug: str
    titulo: str
    forca: str
    requer_supervisao: bool
    condicao_metrica: dict | None = None
    prioridade: int = 100


# -------------------------------------------------------------------------
# Gate de escalonamento (human-in-the-loop)
# -------------------------------------------------------------------------

async def avaliar_gatilhos(
    pool: asyncpg.Pool,
    texto_usuario: str,
) -> ResultadoGate:
    """
    Avalia o texto do usuário contra os gatilhos de escalonamento.

    Retorna ResultadoGate com bloqueado=True se um gatilho crítico for detectado.
    Sinais de transtorno alimentar, risco hidroeletrolítico, uso off-label,
    meta insegura ou gestação/lactação → bloquear ou encaminhar.
    """
    alvo = texto_usuario.lower()
    async with pool.acquire() as con:
        gatilhos = await con.fetch(
            "SELECT tipo, acao, palavras_chave FROM gatilho_escalonamento"
        )

    for g in gatilhos:
        palavras = g["palavras_chave"] or []
        for termo in palavras:
            if termo.lower() in alvo:
                bloqueado = g["acao"] in ("bloquear", "encaminhar_profissional")
                logger.warning(
                    "Gatilho detectado: tipo=%s acao=%s termo='%s'",
                    g["tipo"],
                    g["acao"],
                    termo,
                )
                return ResultadoGate(bloqueado, g["tipo"], g["acao"])

    return ResultadoGate(False, None, None)


# -------------------------------------------------------------------------
# Recuperação híbrida
# -------------------------------------------------------------------------

async def recuperar(
    pool: asyncpg.Pool,
    consulta: str,
    contextos: Sequence[str] | None = None,
    incluir_supervisao: bool = False,
    k: int = 6,
) -> list[ChunkRecuperado]:
    """
    Busca vetorial filtrada por contexto e pelo gate de governança.

    incluir_supervisao=False respeita vw_chunk_servivel:
    conteúdo que exige profissional não é servido a fluxos autônomos.

    RF-04: recuperar() retorna top-k filtrado por contexto e pelo gate de supervisão.
    RF-08: chunks de supervisão não aparecem quando incluir_supervisao=False.
    """
    [vetor] = await embed_fn([consulta])

    async with pool.acquire() as con:
        linhas = await con.fetch(
            """
            SELECT id, texto, requer_supervisao_medica,
                   dominio_slug, contexto_slugs, nivel_evidencia,
                   embedding <=> $1::vector AS distancia
            FROM chunk_conhecimento
            WHERE nivel_evidencia <> 'nao_verificado'
              AND ($2::boolean OR requer_supervisao_medica = FALSE)
              AND ($3::text[] IS NULL OR contexto_slugs && $3::text[])
            ORDER BY embedding <=> $1::vector
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
            nivel_evidencia=r["nivel_evidencia"],
        )
        for r in linhas
    ]


async def recuperar_com_trigram(
    pool: asyncpg.Pool,
    consulta: str,
    contextos: Sequence[str] | None = None,
    incluir_supervisao: bool = False,
    k: int = 6,
    trigram_weight: float = 0.3,
) -> list[ChunkRecuperado]:
    """
    Recuperação híbrida: vetorial + reordenação por trigram (pg_trgm).

    Combina distância vetorial com similaridade trigram para melhorar
    a recuperação de termos exatos (ex.: nomes de fármacos, siglas).
    """
    [vetor] = await embed_fn([consulta])
    consulta_lower = consulta.lower()

    async with pool.acquire() as con:
        linhas = await con.fetch(
            """
            SELECT id, texto, requer_supervisao_medica,
                   dominio_slug, contexto_slugs, nivel_evidencia,
                   embedding <=> $1::vector AS dist_vetorial,
                   similarity(LOWER(texto), $5) AS sim_trigram
            FROM chunk_conhecimento
            WHERE nivel_evidencia <> 'nao_verificado'
              AND ($2::boolean OR requer_supervisao_medica = FALSE)
              AND ($3::text[] IS NULL OR contexto_slugs && $3::text[])
            ORDER BY (embedding <=> $1::vector) * (1 - $6) - similarity(LOWER(texto), $5) * $6
            LIMIT $4
            """,
            vetor,
            incluir_supervisao,
            list(contextos) if contextos else None,
            k,
            consulta_lower,
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
            nivel_evidencia=r["nivel_evidencia"],
        )
        for r in linhas
    ]


# -------------------------------------------------------------------------
# Camada de regras: recomendações elegíveis por contexto
# -------------------------------------------------------------------------

async def recomendacoes_por_contexto(
    pool: asyncpg.Pool,
    contexto_slug: str,
) -> list[RecomendacaoElegivel]:
    """
    Retorna recomendações elegíveis para um contexto clínico.

    RF-05: dado contexto + condição de métrica, retorna recomendações elegíveis.
    """
    async with pool.acquire() as con:
        rows = await con.fetch(
            """
            SELECT r.id::text, r.slug, r.titulo, r.forca,
                   r.requer_supervisao_medica,
                   rr.condicao_metrica, rr.prioridade
            FROM regra_recomendacao rr
            JOIN recomendacao r ON r.id = rr.recomendacao_id AND r.ativo
            JOIN contexto_clinico c ON c.id = rr.contexto_id
            WHERE c.slug = $1 AND rr.ativo
            ORDER BY rr.prioridade
            """,
            contexto_slug,
        )

    return [
        RecomendacaoElegivel(
            id=r["id"],
            slug=r["slug"],
            titulo=r["titulo"],
            forca=r["forca"],
            requer_supervisao=r["requer_supervisao_medica"],
            condicao_metrica=json.loads(r["condicao_metrica"]) if r["condicao_metrica"] else None,
            prioridade=r["prioridade"],
        )
        for r in rows
    ]


# -------------------------------------------------------------------------
# Avaliação de condição de métrica (regra declarativa JSONB)
# -------------------------------------------------------------------------

def avaliar_condicao_metrica(
    condicao: dict | None,
    metricas: dict[str, float],
) -> bool:
    """
    Avalia uma condição declarativa JSONB contra as métricas do usuário.

    Formato suportado:
      {"all": [{"biomarcador": "rca", "op": ">", "valor": 0.5}]}
      {"any": [{"biomarcador": "imc", "op": ">=", "valor": 30}]}

    RF-05: rca > 0.5 em perda_acelerada torna elegível a recomendação de pele.
    """
    if condicao is None:
        return True  # Sem condição = sempre elegível

    def avaliar_regra(r: dict) -> bool:
        bio = r.get("biomarcador", "")
        op = r.get("op", "==")
        valor = r.get("valor")
        metrica_val = metricas.get(bio)

        if metrica_val is None:
            return False  # Métrica não disponível → não elegível

        ops = {
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
        }
        fn = ops.get(op)
        return fn(metrica_val, valor) if fn else False

    if "all" in condicao:
        return all(avaliar_regra(r) for r in condicao["all"])
    if "any" in condicao:
        return any(avaliar_regra(r) for r in condicao["any"])

    return True


async def recomendacoes_elegiveis_por_metrica(
    pool: asyncpg.Pool,
    contexto_slug: str,
    metricas: dict[str, float],
    incluir_supervisao: bool = False,
) -> list[RecomendacaoElegivel]:
    """
    Filtra recomendações do contexto pelas condições de métrica do usuário.

    RF-05: dada rca > 0.5 em perda_acelerada, a recomendação de pele é elegível.
    """
    todas = await recomendacoes_por_contexto(pool, contexto_slug)
    elegiveis = []

    for rec in todas:
        if not incluir_supervisao and rec.requer_supervisao:
            continue
        if avaliar_condicao_metrica(rec.condicao_metrica, metricas):
            elegiveis.append(rec)

    return elegiveis
