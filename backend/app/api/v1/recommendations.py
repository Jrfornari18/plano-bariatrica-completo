"""
Endpoints de recomendação (RF-05, RF-06).
POST /api/v1/recommendations
POST /api/v1/recommendations/{id}/feedback
"""
from fastapi import APIRouter, HTTPException
from app.models.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    FeedbackRequest,
    FeedbackResponse,
)
from app.services import recommendation_service
from app.repositories import recommendation_repo
from app.core.logging import get_logger, new_request_id

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
logger = get_logger(__name__)


@router.post("", response_model=RecommendationResponse, status_code=200)
async def create_recommendation(req: RecommendationRequest):
    """
    RF-05: Orquestra o pipeline RAG híbrido e retorna o treino estruturado.
    Requisição válida → HTTP 200 com JSON do treino.
    Requisição inválida → HTTP 422 (Pydantic v2 automático).
    """
    rid = new_request_id()
    logger.info("Nova recomendação solicitada: perfil_id=%s, intencao='%s...'", req.perfil_id, req.intencao[:50])

    if req.perfil_id is None and req.nivel is None:
        # Aceitar sem perfil_id — usar defaults
        pass

    try:
        response = await recommendation_service.recomendar(req)
        return response
    except Exception as exc:
        logger.error("Erro ao gerar recomendação: %s", exc)
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar recomendação: {str(exc)}")


@router.post("/{rec_id}/feedback", response_model=FeedbackResponse, status_code=200)
async def submit_feedback(rec_id: int, body: FeedbackRequest):
    """
    RF-06: Registra nota 1–5 para uma recomendação.
    Rejeita valores fora de 1–5 (validação Pydantic).
    """
    updated = await recommendation_repo.update_feedback(rec_id, body.nota)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Recomendação {rec_id} não encontrada")
    return FeedbackResponse(recomendacao_id=rec_id, nota=body.nota)
