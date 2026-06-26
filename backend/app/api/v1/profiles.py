"""
Endpoints de perfil de usuário (RF-07).
POST /api/v1/profiles
GET  /api/v1/profiles/{id}
"""
from fastapi import APIRouter, HTTPException
from app.models.profile import ProfileCreate, ProfileResponse
from app.repositories import profile_repo
from app.core.logging import get_logger

router = APIRouter(prefix="/profiles", tags=["profiles"])
logger = get_logger(__name__)


@router.post("", response_model=ProfileResponse, status_code=201)
async def create_profile(profile: ProfileCreate):
    """RF-07: Cria um novo perfil de usuário (inclui métricas do BodyScan)."""
    profile_id = await profile_repo.create_profile(profile)
    created = await profile_repo.get_profile(profile_id)
    if not created:
        raise HTTPException(status_code=500, detail="Falha ao recuperar perfil criado")
    return ProfileResponse(**created)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int):
    """RF-07: Retorna um perfil pelo ID."""
    profile = await profile_repo.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Perfil {profile_id} não encontrado")
    return ProfileResponse(**profile)
