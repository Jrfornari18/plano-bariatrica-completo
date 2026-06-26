"""
conhecimento.py — Router de busca de conhecimento (uso interno).

GET /v1/conhecimento/buscar — Busca híbrida na base de conhecimento.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query

from ..database import get_pool
from ..models.schemas import BuscarResponse, ChunkResponse
from ..services.recuperacao import recuperar

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/conhecimento", tags=["conhecimento"])


@router.get(
    "/buscar",
    response_model=BuscarResponse,
    summary="Busca híbrida na base de conhecimento (interno)",
)
async def get_buscar(
    q: str = Query(..., description="Consulta de busca"),
    contextos: list[str] | None = Query(default=None, description="Filtro de contextos"),
    k: int = Query(default=6, ge=1, le=20),
    incluir_supervisao: bool = Query(default=False),
    pool=Depends(get_pool),
):
    chunks = await recuperar(
        pool=pool,
        consulta=q,
        contextos=contextos,
        incluir_supervisao=incluir_supervisao,
        k=k,
    )
    return BuscarResponse(
        chunks=[
            ChunkResponse(
                id=c.id,
                texto=c.texto,
                distancia=c.distancia,
                requer_supervisao=c.requer_supervisao,
                dominio_slug=c.dominio_slug,
                contexto_slugs=c.contexto_slugs,
                nivel_evidencia=c.nivel_evidencia,
            )
            for c in chunks
        ],
        total=len(chunks),
    )
