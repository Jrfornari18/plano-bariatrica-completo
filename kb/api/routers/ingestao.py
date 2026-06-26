"""
ingestao.py — Router de ingestão de documentos.

POST /v1/ingestao/documento — Ingere um documento e gera embeddings.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ..database import get_pool
from ..models.schemas import IngestaoDocumentoRequest, IngestaoResponse
from ..services.ingestao import ingerir_documento

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/ingestao", tags=["ingestao"])


@router.post(
    "/documento",
    response_model=IngestaoResponse,
    summary="Ingere documento e gera embeddings",
)
async def post_ingestao_documento(
    req: IngestaoDocumentoRequest,
    pool=Depends(get_pool),
):
    try:
        n = await ingerir_documento(pool, req.documento_id)
        return IngestaoResponse(documento_id=req.documento_id, chunks_gerados=n)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("Erro na ingestão de %s: %s", req.documento_id, exc)
        raise HTTPException(status_code=500, detail=f"Erro na ingestão: {exc}")
