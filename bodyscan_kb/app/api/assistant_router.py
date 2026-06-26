"""
Router — Assistente / Orquestração (Épico E).
Endpoints: /assistant/{id}/retrieve, /assistant/feedback
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.l3_subject import Usuario
from app.schemas.user_memory_schemas import (
    FeedbackRequest,
    RetrieveRequest,
    RetrieveResponse,
)
from app.services.assistant import get_assistant_service

router = APIRouter()
logger = logging.getLogger(__name__)


# ── POST /assistant/{id}/retrieve ─────────────────────────────────────────────
@router.post("/{usuario_id}/retrieve", response_model=RetrieveResponse)
async def recuperar_contexto(
    usuario_id: str,
    request: RetrieveRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    RF-E1 — Recuperação orquestrada.
    Combina: snapshot recente + memórias ativas + RAG + expansão cross-domínio.
    RF-E2 — Aplica vínculos 'validado' como restrições/prioridades.
    RF-E3 — Registra recuperacao_log automaticamente.
    """
    usuario = await db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            404, {"detail": "Usuário não encontrado", "code": "USER_NOT_FOUND"}
        )

    service = get_assistant_service()
    return await service.retrieve(db, usuario_id, request)


# ── POST /assistant/feedback ──────────────────────────────────────────────────
@router.post("/feedback")
async def registrar_feedback(
    data: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """RF-E3 — Registrar feedback do usuário em um log de recuperação."""
    service = get_assistant_service()
    ok = await service.registrar_feedback(db, data.log_id, data.feedback)
    if not ok:
        raise HTTPException(
            404, {"detail": "Log de recuperação não encontrado", "code": "LOG_NOT_FOUND"}
        )
    return {"status": "ok", "log_id": data.log_id, "feedback": data.feedback}
