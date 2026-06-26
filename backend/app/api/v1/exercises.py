"""
Endpoints do catálogo de exercícios (RF-08).
GET /api/v1/exercises
GET /api/v1/exercises/{id}
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.models.exercise import ExerciseDetail, ExerciseListResponse
from app.repositories import exercise_repo
from app.core.logging import get_logger

router = APIRouter(prefix="/exercises", tags=["exercises"])
logger = get_logger(__name__)


@router.get("", response_model=ExerciseListResponse)
async def list_exercises(
    modalidade: Optional[str] = Query(None, description="Slug da modalidade (ex: funcional, musculacao)"),
    nivel: Optional[str] = Query(None, description="Nível: iniciante | intermediario | avancado"),
    objetivo: Optional[str] = Query(None, description="Objetivo (ex: emagrecimento, hipertrofia)"),
    equipamento: Optional[str] = Query(None, description="Nome do equipamento"),
):
    """RF-08: Lista exercícios com filtros combináveis."""
    exercises = await exercise_repo.list_exercises(
        modalidade=modalidade,
        nivel=nivel,
        objetivo=objetivo,
        equipamento=equipamento,
    )
    return ExerciseListResponse(total=len(exercises), exercicios=[ExerciseDetail(**ex) for ex in exercises])


@router.get("/{exercise_id}", response_model=ExerciseDetail)
async def get_exercise(exercise_id: int):
    """RF-08: Detalhe de um exercício com músculos, equipamentos, objetivos e alternativas."""
    exercise = await exercise_repo.get_exercise_by_id(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail=f"Exercício {exercise_id} não encontrado")
    return ExerciseDetail(**exercise)
