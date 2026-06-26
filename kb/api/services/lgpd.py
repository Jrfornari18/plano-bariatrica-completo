"""
lgpd.py — Conformidade LGPD: anonimização, direito ao esquecimento e exportação.

LGPD (Lei 13.709/2018) — Direitos do titular:
  - Art. 18 I: Confirmação de existência de tratamento
  - Art. 18 II: Acesso aos dados
  - Art. 18 IV: Anonimização ou bloqueio de dados desnecessários
  - Art. 18 VI: Eliminação dos dados pessoais

RNF-02: Sem PII direta — apenas pseudônimo.
RNF-03: Consentimento LGPD verificado antes de persistir métricas.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

import asyncpg

logger = logging.getLogger(__name__)


async def exportar_dados_usuario(
    pool: asyncpg.Pool,
    pseudonimo: str,
) -> dict:
    """
    Art. 18 II — Acesso aos dados do titular.
    Retorna todos os dados associados ao pseudônimo.
    """
    async with pool.acquire() as con:
        perfil = await con.fetchrow(
            "SELECT id, pseudonimo, contexto_id, consentimento_lgpd, criado_em FROM perfil_usuario WHERE pseudonimo = $1",
            pseudonimo,
        )
        if not perfil:
            return {"erro": "Perfil não encontrado"}

        perfil_id = perfil["id"]

        metricas = await con.fetch(
            """
            SELECT b.slug AS biomarcador, pm.valor, pm.medido_em
            FROM perfil_metrica pm
            JOIN biomarcador b ON b.id = pm.biomarcador_id
            WHERE pm.perfil_id = $1
            ORDER BY pm.medido_em DESC
            """,
            perfil_id,
        )

        logs = await con.fetch(
            """
            SELECT id, modelo_gerador, houve_escalonamento, tipo_alerta_disparado, criado_em
            FROM log_recomendacao
            WHERE perfil_id = $1
            ORDER BY criado_em DESC
            LIMIT 50
            """,
            perfil_id,
        )

    return {
        "pseudonimo": pseudonimo,
        "consentimento_lgpd": perfil["consentimento_lgpd"],
        "criado_em": str(perfil["criado_em"]),
        "metricas": [
            {"biomarcador": m["biomarcador"], "valor": float(m["valor"]), "medido_em": str(m["medido_em"])}
            for m in metricas
        ],
        "logs_recomendacao": [
            {
                "id": str(l["id"]),
                "modelo": l["modelo_gerador"],
                "escalonamento": l["houve_escalonamento"],
                "criado_em": str(l["criado_em"]),
            }
            for l in logs
        ],
    }


async def revogar_consentimento(
    pool: asyncpg.Pool,
    pseudonimo: str,
) -> dict:
    """
    Art. 18 IV/VI — Revogação de consentimento e anonimização.
    Remove métricas e anonimiza o pseudônimo.
    """
    async with pool.acquire() as con:
        perfil = await con.fetchrow(
            "SELECT id FROM perfil_usuario WHERE pseudonimo = $1", pseudonimo
        )
        if not perfil:
            return {"erro": "Perfil não encontrado"}

        perfil_id = perfil["id"]

        # Remove métricas (dados pessoais de saúde)
        n_metricas = await con.fetchval(
            "DELETE FROM perfil_metrica WHERE perfil_id = $1 RETURNING COUNT(*)",
            perfil_id,
        )

        # Anonimiza pseudônimo e revoga consentimento
        novo_pseudonimo = f"anonimizado_{uuid.uuid4().hex[:8]}"
        await con.execute(
            """
            UPDATE perfil_usuario
            SET pseudonimo = $1, consentimento_lgpd = FALSE
            WHERE id = $2
            """,
            novo_pseudonimo,
            perfil_id,
        )

    logger.info(
        "LGPD: consentimento revogado para pseudonimo=%s -> %s, metricas_removidas=%s",
        pseudonimo,
        novo_pseudonimo,
        n_metricas,
    )

    return {
        "ok": True,
        "metricas_removidas": n_metricas or 0,
        "pseudonimo_anonimizado": novo_pseudonimo,
        "data_revogacao": datetime.utcnow().isoformat(),
    }


async def verificar_consentimento(
    pool: asyncpg.Pool,
    pseudonimo: str,
) -> bool:
    """
    Art. 18 I — Confirmação de existência e status do consentimento.
    """
    async with pool.acquire() as con:
        row = await con.fetchrow(
            "SELECT consentimento_lgpd FROM perfil_usuario WHERE pseudonimo = $1",
            pseudonimo,
        )
    return bool(row and row["consentimento_lgpd"])
