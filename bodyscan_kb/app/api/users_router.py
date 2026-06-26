"""
Router — Usuários (Épico C).
Endpoints: /users, /users/{id}/snapshots
"""
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.l3_subject import PerfilFisiologicoSnapshot, Usuario
from app.schemas.user_memory_schemas import (
    SnapshotCreate,
    SnapshotResponse,
    UsuarioCreate,
    UsuarioResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


# ── POST /users ───────────────────────────────────────────────────────────────
@router.post("", response_model=UsuarioResponse, status_code=201)
async def criar_usuario(
    data: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-C1 — Criar usuário com objetivo_principal e restricoes."""
    usuario = Usuario(**data.model_dump())
    db.add(usuario)
    await db.flush()
    await db.refresh(usuario)
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obter_usuario(
    usuario_id: str,
    db: AsyncSession = Depends(get_db),
):
    usuario = await db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, {"detail": "Usuário não encontrado", "code": "USER_NOT_FOUND"})
    return usuario


# ── POST /users/{id}/snapshots ────────────────────────────────────────────────
@router.post("/{usuario_id}/snapshots", response_model=SnapshotResponse, status_code=201)
async def registrar_snapshot(
    usuario_id: str,
    data: SnapshotCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    RF-C2 — Registrar snapshot fisiológico imutável, vinculável a scan_id do BodyScan.
    Snapshots são imutáveis após criação — não há endpoint de atualização.
    """
    usuario = await db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, {"detail": "Usuário não encontrado", "code": "USER_NOT_FOUND"})

    snapshot = PerfilFisiologicoSnapshot(
        usuario_id=usuario_id,
        **data.model_dump(),
    )
    db.add(snapshot)
    await db.flush()
    await db.refresh(snapshot)
    return snapshot


# ── GET /users/{id}/snapshots ─────────────────────────────────────────────────
@router.get("/{usuario_id}/snapshots", response_model=list[SnapshotResponse])
async def listar_snapshots(
    usuario_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """RF-C3 — Série temporal de snapshots ordenada por data (mais recente primeiro)."""
    usuario = await db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(404, {"detail": "Usuário não encontrado", "code": "USER_NOT_FOUND"})

    stmt = (
        select(PerfilFisiologicoSnapshot)
        .where(PerfilFisiologicoSnapshot.usuario_id == usuario_id)
        .order_by(PerfilFisiologicoSnapshot.data_medicao.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
