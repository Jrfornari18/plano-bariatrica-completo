"""
lgpd.py — Router de conformidade LGPD.

GET  /v1/lgpd/{pseudonimo}/dados   — Exportação de dados (Art. 18 II)
POST /v1/lgpd/{pseudonimo}/revogar — Revogação de consentimento (Art. 18 IV/VI)
GET  /v1/lgpd/{pseudonimo}/status  — Status de consentimento (Art. 18 I)
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ..database import get_pool
from ..services.lgpd import exportar_dados_usuario, revogar_consentimento, verificar_consentimento

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/lgpd", tags=["lgpd"])


@router.get(
    "/{pseudonimo}/dados",
    summary="Exporta todos os dados do titular (Art. 18 II LGPD)",
)
async def get_dados_usuario(pseudonimo: str, pool=Depends(get_pool)):
    """Retorna todos os dados associados ao pseudônimo do titular."""
    return await exportar_dados_usuario(pool, pseudonimo)


@router.post(
    "/{pseudonimo}/revogar",
    summary="Revoga consentimento e anonimiza dados (Art. 18 IV/VI LGPD)",
)
async def post_revogar_consentimento(pseudonimo: str, pool=Depends(get_pool)):
    """Remove métricas pessoais e anonimiza o pseudônimo do titular."""
    resultado = await revogar_consentimento(pool, pseudonimo)
    if "erro" in resultado:
        raise HTTPException(status_code=404, detail=resultado["erro"])
    return resultado


@router.get(
    "/{pseudonimo}/status",
    summary="Verifica status de consentimento LGPD (Art. 18 I LGPD)",
)
async def get_status_consentimento(pseudonimo: str, pool=Depends(get_pool)):
    """Confirma existência de tratamento e status do consentimento."""
    consentimento = await verificar_consentimento(pool, pseudonimo)
    return {"pseudonimo": pseudonimo, "consentimento_ativo": consentimento}
