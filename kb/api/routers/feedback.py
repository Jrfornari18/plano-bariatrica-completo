"""
feedback.py — Router de feedback de recomendações.

POST /v1/feedback — Persiste feedback do usuário vinculado ao log.
RF-10: Feedback persistido e vinculado ao log_recomendacao.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from ..database import get_pool
from ..models.schemas import FeedbackRequest, FeedbackResponse
from ..services.auditoria import registrar_feedback

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/feedback", tags=["feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    summary="Registra feedback sobre recomendação emitida",
)
async def post_feedback(
    req: FeedbackRequest,
    pool=Depends(get_pool),
):
    try:
        feedback_id = await registrar_feedback(
            pool=pool,
            log_id=req.log_id,
            util=req.util,
            comentario=req.comentario,
        )
        return FeedbackResponse(feedback_id=feedback_id)
    except Exception as exc:
        logger.error("Erro ao registrar feedback: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erro ao registrar feedback: {exc}")
