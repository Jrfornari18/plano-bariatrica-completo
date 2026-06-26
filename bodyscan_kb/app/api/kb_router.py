"""
Router — Base de Conhecimento (Épico A + B).
Endpoints: /kb/sources, /kb/chunks, /kb/concepts, /kb/relations, /kb/search
"""
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.l1_knowledge import Concept, ConceptRelation, KnowledgeChunk, KnowledgeSource
from app.models.l2_domain import (
    FisiologiaMarcador,
    NutricaoAlimento,
    NutricaoProtocolo,
    TreinoExercicio,
    TreinoProtocolo,
)
from app.schemas.kb_schemas import (
    ConceptCreate,
    ConceptRelationCreate,
    ConceptRelationResponse,
    ConceptResponse,
    FisiologiaMarcadorCreate,
    KnowledgeChunkCreate,
    KnowledgeChunkResponse,
    KnowledgeSourceCreate,
    KnowledgeSourceResponse,
    NutricaoAlimentoCreate,
    NutricaoProtocoloCreate,
    NutricaoProtocoloResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    TreinoExercicioCreate,
    TreinoProtocoloCreate,
    TreinoProtocoloResponse,
)
from app.services.embedding import get_embedding_provider
from app.services.retrieval import get_retrieval_service

router = APIRouter()
logger = logging.getLogger(__name__)


# ── POST /kb/sources ──────────────────────────────────────────────────────────
@router.post("/sources", response_model=KnowledgeSourceResponse, status_code=201)
async def criar_source(
    data: KnowledgeSourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-A1 — Persistir knowledge_source."""
    source = KnowledgeSource(**data.model_dump())
    db.add(source)
    await db.flush()
    await db.refresh(source)
    return source


@router.get("/sources", response_model=list[KnowledgeSourceResponse])
async def listar_sources(
    dominio: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(KnowledgeSource)
    if dominio:
        stmt = stmt.where(KnowledgeSource.dominio == dominio)
    result = await db.execute(stmt)
    return result.scalars().all()


# ── POST /kb/chunks ───────────────────────────────────────────────────────────
@router.post("/chunks", response_model=KnowledgeChunkResponse, status_code=201)
async def criar_chunk(
    data: KnowledgeChunkCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-A2 — Persistir knowledge_chunk com embedding gerado automaticamente."""
    provider = get_embedding_provider()

    # Verificar se source existe
    source = await db.get(KnowledgeSource, data.source_id)
    if not source:
        raise HTTPException(
            status_code=404,
            detail={"detail": "knowledge_source não encontrado", "code": "SOURCE_NOT_FOUND"},
        )

    # Gerar embedding
    embedding = await provider.embed(data.conteudo)

    chunk = KnowledgeChunk(
        source_id=data.source_id,
        dominio=data.dominio,
        ordem=data.ordem,
        conteudo=data.conteudo,
        tokens=data.tokens or len(data.conteudo.split()),
        embedding=embedding,
        embedding_model_version=provider.model_version,
        metadata_=data.metadata_ or {},
    )
    db.add(chunk)
    await db.flush()
    await db.refresh(chunk)
    return KnowledgeChunkResponse(
        id=chunk.id,
        source_id=chunk.source_id,
        dominio=chunk.dominio,
        ordem=chunk.ordem,
        conteudo=chunk.conteudo,
        tokens=chunk.tokens,
        embedding_model_version=chunk.embedding_model_version,
        metadata=chunk.metadata_,
    )


# ── POST /kb/concepts ─────────────────────────────────────────────────────────
@router.post("/concepts", response_model=ConceptResponse, status_code=201)
async def criar_concept(
    data: ConceptCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-A3 — Persistir concept único por (dominio, nome_canonico)."""
    # Verificar unicidade
    stmt = select(Concept).where(
        Concept.dominio == data.dominio,
        Concept.nome_canonico == data.nome_canonico,
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"detail": "Conceito já existe neste domínio", "code": "CONCEPT_DUPLICATE"},
        )

    # Gerar embedding do conceito
    provider = get_embedding_provider()
    embedding = await provider.embed(f"{data.nome}: {data.definicao or ''}")

    concept = Concept(
        dominio=data.dominio,
        tipo_conceito=data.tipo_conceito,
        nome=data.nome,
        nome_canonico=data.nome_canonico,
        definicao=data.definicao,
        aliases=data.aliases or [],
        embedding=embedding,
    )
    db.add(concept)
    await db.flush()
    await db.refresh(concept)
    return concept


@router.get("/concepts", response_model=list[ConceptResponse])
async def listar_concepts(
    dominio: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Concept)
    if dominio:
        stmt = stmt.where(Concept.dominio == dominio)
    result = await db.execute(stmt)
    return result.scalars().all()


# ── POST /kb/relations ────────────────────────────────────────────────────────
@router.post("/relations", response_model=ConceptRelationResponse, status_code=201)
async def criar_relation(
    data: ConceptRelationCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-A4 — Criar relação intra ou cross-domínio entre conceitos."""
    # Verificar existência dos conceitos
    for cid in [data.concept_origem_id, data.concept_destino_id]:
        if not await db.get(Concept, cid):
            raise HTTPException(
                status_code=404,
                detail={"detail": f"Conceito {cid} não encontrado", "code": "CONCEPT_NOT_FOUND"},
            )

    relation = ConceptRelation(**data.model_dump())
    db.add(relation)
    await db.flush()
    await db.refresh(relation)
    return relation


@router.get("/relations", response_model=list[ConceptRelationResponse])
async def listar_relations(
    cross_domain_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ConceptRelation)
    if cross_domain_only:
        stmt = stmt.where(
            ConceptRelation.dominio_origem != ConceptRelation.dominio_destino
        )
    result = await db.execute(stmt)
    return result.scalars().all()


# ── GET /kb/search ────────────────────────────────────────────────────────────
@router.get("/search", response_model=SearchResponse)
async def busca_vetorial(
    q: str = Query(..., description="Texto da query"),
    dominio: str | None = Query(None),
    top_k: int = Query(5, ge=1, le=50),
    threshold: float = Query(0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
):
    """RF-A5 — Busca vetorial filtrada por domínio."""
    service = get_retrieval_service()
    results = await service.search(
        db=db,
        query=q,
        dominio=dominio,
        top_k=top_k,
        similarity_threshold=threshold,
    )
    return SearchResponse(
        query=q,
        dominio=dominio,
        results=[
            SearchResultItem(
                chunk_id=r.chunk_id,
                source_id=r.source_id,
                dominio=r.dominio,
                conteudo=r.conteudo,
                score=r.score,
                metadata=r.metadata,
            )
            for r in results
        ],
        total=len(results),
    )


# ── L2 — Especializações ──────────────────────────────────────────────────────
@router.post("/domain/fisiologia-marcador", status_code=201)
async def criar_marcador(
    data: FisiologiaMarcadorCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-B1, RF-B3 — Criar marcador fisiológico (IMC, RCQ, RCA, % gordura)."""
    if not await db.get(Concept, data.concept_id):
        raise HTTPException(404, {"detail": "Conceito não encontrado", "code": "CONCEPT_NOT_FOUND"})
    marcador = FisiologiaMarcador(**data.model_dump())
    db.add(marcador)
    await db.flush()
    return {"id": marcador.concept_id, "status": "created"}


@router.post("/domain/treino-exercicio", status_code=201)
async def criar_exercicio(
    data: TreinoExercicioCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-B1 — Criar exercício de treino."""
    if not await db.get(Concept, data.concept_id):
        raise HTTPException(404, {"detail": "Conceito não encontrado", "code": "CONCEPT_NOT_FOUND"})
    exercicio = TreinoExercicio(**data.model_dump())
    db.add(exercicio)
    await db.flush()
    return {"id": exercicio.concept_id, "status": "created"}


@router.post("/domain/treino-protocolo", response_model=TreinoProtocoloResponse, status_code=201)
async def criar_treino_protocolo(
    data: TreinoProtocoloCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-B2 — Criar protocolo de treino."""
    protocolo = TreinoProtocolo(**data.model_dump())
    db.add(protocolo)
    await db.flush()
    await db.refresh(protocolo)
    return protocolo


@router.post("/domain/nutricao-alimento", status_code=201)
async def criar_alimento(
    data: NutricaoAlimentoCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-B1 — Criar alimento."""
    if not await db.get(Concept, data.concept_id):
        raise HTTPException(404, {"detail": "Conceito não encontrado", "code": "CONCEPT_NOT_FOUND"})
    alimento = NutricaoAlimento(**data.model_dump())
    db.add(alimento)
    await db.flush()
    return {"id": alimento.concept_id, "status": "created"}


@router.post("/domain/nutricao-protocolo", response_model=NutricaoProtocoloResponse, status_code=201)
async def criar_nutricao_protocolo(
    data: NutricaoProtocoloCreate,
    db: AsyncSession = Depends(get_db),
):
    """RF-B2 — Criar protocolo nutricional."""
    protocolo = NutricaoProtocolo(**data.model_dump())
    db.add(protocolo)
    await db.flush()
    await db.refresh(protocolo)
    return protocolo
