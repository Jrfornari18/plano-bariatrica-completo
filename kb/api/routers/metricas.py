"""
metricas.py — Router de métricas de observabilidade.

GET /v1/metricas — Métricas de uso da API (latência, escalonamentos, feedback).
RNF-05: Métricas de latência e taxa de escalonamento disponíveis.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from ..database import get_pool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/metricas", tags=["observabilidade"])


@router.get(
    "",
    summary="Métricas de uso e observabilidade da API KB",
)
async def get_metricas(pool=Depends(get_pool)):
    """
    Retorna métricas agregadas:
    - Total de recomendações emitidas
    - Taxa de escalonamento
    - Feedback positivo/negativo
    - Distribuição por modelo
    """
    async with pool.acquire() as con:
        total_logs = await con.fetchval("SELECT COUNT(*) FROM log_recomendacao")
        total_escalonamentos = await con.fetchval(
            "SELECT COUNT(*) FROM log_recomendacao WHERE houve_escalonamento = TRUE"
        )
        total_feedback = await con.fetchval("SELECT COUNT(*) FROM feedback_recomendacao")
        feedback_positivo = await con.fetchval(
            "SELECT COUNT(*) FROM feedback_recomendacao WHERE util = TRUE"
        )
        feedback_negativo = await con.fetchval(
            "SELECT COUNT(*) FROM feedback_recomendacao WHERE util = FALSE"
        )

        por_modelo = await con.fetch(
            """
            SELECT modelo_gerador, COUNT(*) AS total
            FROM log_recomendacao
            GROUP BY modelo_gerador
            ORDER BY total DESC
            """
        )

        por_alerta = await con.fetch(
            """
            SELECT tipo_alerta_disparado::text AS tipo, COUNT(*) AS total
            FROM log_recomendacao
            WHERE houve_escalonamento = TRUE AND tipo_alerta_disparado IS NOT NULL
            GROUP BY tipo_alerta_disparado
            ORDER BY total DESC
            """
        )

        total_perfis = await con.fetchval("SELECT COUNT(*) FROM perfil_usuario")
        total_chunks = await con.fetchval("SELECT COUNT(*) FROM chunk_conhecimento")
        total_documentos = await con.fetchval("SELECT COUNT(*) FROM documento_conhecimento")

    taxa_escalonamento = (
        round(total_escalonamentos / total_logs * 100, 1) if total_logs > 0 else 0
    )
    taxa_feedback_positivo = (
        round(feedback_positivo / total_feedback * 100, 1) if total_feedback > 0 else 0
    )

    return {
        "recomendacoes": {
            "total": total_logs,
            "escalonamentos": total_escalonamentos,
            "taxa_escalonamento_pct": taxa_escalonamento,
        },
        "feedback": {
            "total": total_feedback,
            "positivo": feedback_positivo,
            "negativo": feedback_negativo,
            "taxa_positivo_pct": taxa_feedback_positivo,
        },
        "por_modelo": [{"modelo": r["modelo_gerador"], "total": r["total"]} for r in por_modelo],
        "alertas_escalonamento": [{"tipo": r["tipo"], "total": r["total"]} for r in por_alerta],
        "base_conhecimento": {
            "documentos": total_documentos,
            "chunks": total_chunks,
            "perfis_usuarios": total_perfis,
        },
    }
