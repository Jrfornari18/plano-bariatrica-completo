"""
Router — Memória (Épico D).
Endpoints: /memory/{id}/episodes, /memory/{id}/semantic, /memory/{id}/cross-links
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.l3_subject import Usuario
from app.schemas.user_memory_schemas import (
    EpisodioCreate,
    EpisodioResponse,
    SemanticaCreate,
    SemanticaResponse,
    VinculoCrossCreate,
    VinculoCrossResponse,
)
from app.services.memory import get_memory_service

router = APIRouter()
logger = logging.getLogger(__name__)


async def _verificar_usuario(usuario_id: str, db: AsyncSession) -> Usuario:
    usuario = await db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(
            404, {"detail": "Usuário não encontrado", "code": "USER_NOT_FOUND"}
        )
    return usuario


# ── POST /memory/{id}/episodes ────────────────────────────────────────────────
@router.post("/{usuario_id}/episodes", response_model=EpisodioResponse, status_code=201)
async def registrar_episodio(
    usuario_id: str,
    data: EpisodioCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-D1 — Registrar evento episódico na linha do tempo do usuário."""
    await _verificar_usuario(usuario_id, db)
    service = get_memory_service()
    episodio = await service.registrar_episodio(db, usuario_id, data)
    return EpisodioResponse(
        id=episodio.id,
        usuario_id=episodio.usuario_id,
        tipo_evento=episodio.tipo_evento,
        dominio=episodio.dominio,
        ref_entidade_tipo=episodio.ref_entidade_tipo,
        ref_entidade_id=episodio.ref_entidade_id,
        payload=episodio.payload,
        ocorrido_em=episodio.ocorrido_em,
    )


@router.get("/{usuario_id}/episodes", response_model=list[EpisodioResponse])
async def listar_episodios(
    usuario_id: str,
    dominio: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Lista episódios do usuário, ordenados por data decrescente."""
    await _verificar_usuario(usuario_id, db)
    service = get_memory_service()
    episodios = await service.listar_episodios(db, usuario_id, dominio, limit)
    return [
        EpisodioResponse(
            id=e.id,
            usuario_id=e.usuario_id,
            tipo_evento=e.tipo_evento,
            dominio=e.dominio,
            ref_entidade_tipo=e.ref_entidade_tipo,
            ref_entidade_id=e.ref_entidade_id,
            payload=e.payload,
            ocorrido_em=e.ocorrido_em,
        )
        for e in episodios
    ]


# ── POST /memory/{id}/semantic ────────────────────────────────────────────────
@router.post("/{usuario_id}/semantic", response_model=SemanticaResponse, status_code=201)
async def registrar_semantica(
    usuario_id: str,
    data: SemanticaCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-D2 — Registrar memória semântica com confiança, validade temporal e embedding."""
    await _verificar_usuario(usuario_id, db)
    service = get_memory_service()
    mem = await service.registrar_semantica(db, usuario_id, data)
    return SemanticaResponse(
        id=mem.id,
        usuario_id=mem.usuario_id,
        dominio=mem.dominio,
        tipo=mem.tipo,
        afirmacao=mem.afirmacao,
        confianca=mem.confianca,
        evidencia_episodios=mem.evidencia_episodios,
        valido_de=mem.valido_de,
        valido_ate=mem.valido_ate,
        ativo=mem.ativo,
        created_at=mem.created_at,
    )


@router.get("/{usuario_id}/semantic", response_model=list[SemanticaResponse])
async def listar_semantica(
    usuario_id: str,
    dominio: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lista memórias semânticas ativas e válidas do usuário."""
    await _verificar_usuario(usuario_id, db)
    service = get_memory_service()
    memorias = await service.listar_semantica_ativa(db, usuario_id, dominio)
    return [
        SemanticaResponse(
            id=m.id,
            usuario_id=m.usuario_id,
            dominio=m.dominio,
            tipo=m.tipo,
            afirmacao=m.afirmacao,
            confianca=m.confianca,
            evidencia_episodios=m.evidencia_episodios,
            valido_de=m.valido_de,
            valido_ate=m.valido_ate,
            ativo=m.ativo,
            created_at=m.created_at,
        )
        for m in memorias
    ]


# ── POST /memory/{id}/cross-links ─────────────────────────────────────────────
@router.post("/{usuario_id}/cross-links", response_model=VinculoCrossResponse, status_code=201)
async def registrar_vinculo(
    usuario_id: str,
    data: VinculoCrossCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    RF-D3 — Registrar vínculo cross-domínio.
    Exige ≥ 2 domínios preenchidos. Status inicia em 'hipotese'.
    """
    await _verificar_usuario(usuario_id, db)
    service = get_memory_service()
    try:
        vinculo = await service.registrar_vinculo(db, usuario_id, data)
    except ValueError as e:
        raise HTTPException(
            422, {"detail": str(e), "code": "CROSS_LINK_VALIDATION_ERROR"}
        )
    return VinculoCrossResponse(
        id=vinculo.id,
        usuario_id=vinculo.usuario_id,
        conceito_fisiologia_id=vinculo.conceito_fisiologia_id,
        conceito_treino_id=vinculo.conceito_treino_id,
        conceito_nutricao_id=vinculo.conceito_nutricao_id,
        tipo_vinculo=vinculo.tipo_vinculo,
        descricao=vinculo.descricao,
        forca=vinculo.forca,
        gerado_por=vinculo.gerado_por,
        evidencia=vinculo.evidencia,
        status=vinculo.status,
        created_at=vinculo.created_at,
    )


@router.get("/{usuario_id}/cross-links", response_model=list[VinculoCrossResponse])
async def listar_vinculos(
    usuario_id: str,
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Lista vínculos cross-domínio do usuário, opcionalmente filtrado por status."""
    await _verificar_usuario(usuario_id, db)
    service = get_memory_service()
    vinculos = await service.listar_vinculos(db, usuario_id, status)
    return [
        VinculoCrossResponse(
            id=v.id,
            usuario_id=v.usuario_id,
            conceito_fisiologia_id=v.conceito_fisiologia_id,
            conceito_treino_id=v.conceito_treino_id,
            conceito_nutricao_id=v.conceito_nutricao_id,
            tipo_vinculo=v.tipo_vinculo,
            descricao=v.descricao,
            forca=v.forca,
            gerado_por=v.gerado_por,
            evidencia=v.evidencia,
            status=v.status,
            created_at=v.created_at,
        )
        for v in vinculos
    ]
