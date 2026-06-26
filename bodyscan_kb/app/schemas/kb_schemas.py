"""
Schemas Pydantic v2 — Base de Conhecimento (L1 e L2).
"""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── KnowledgeSource ───────────────────────────────────────────────────────────
class KnowledgeSourceCreate(BaseModel):
    dominio: str = Field(..., pattern="^(fisiologia|treino|nutricao)$")
    titulo: str
    tipo: str = Field(..., pattern="^(paper|livro|protocolo|diretriz|nota_interna)$")
    autor: str | None = None
    referencia: str | None = None
    ano: int | None = None
    confiabilidade: str = Field(..., pattern="^(primaria|oficial|secundaria)$")
    idioma: str | None = Field(None, max_length=2)


class KnowledgeSourceResponse(KnowledgeSourceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime


# ── KnowledgeChunk ────────────────────────────────────────────────────────────
class KnowledgeChunkCreate(BaseModel):
    source_id: str
    dominio: str = Field(..., pattern="^(fisiologia|treino|nutricao)$")
    ordem: int | None = None
    conteudo: str
    tokens: int | None = None
    metadata_: dict[str, Any] | None = Field(None, alias="metadata")

    model_config = ConfigDict(populate_by_name=True)


class KnowledgeChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    source_id: str
    dominio: str
    ordem: int | None
    conteudo: str
    tokens: int | None
    embedding_model_version: str
    metadata_: dict[str, Any] | None = Field(None, alias="metadata")


# ── Concept ───────────────────────────────────────────────────────────────────
class ConceptCreate(BaseModel):
    dominio: str = Field(..., pattern="^(fisiologia|treino|nutricao)$")
    tipo_conceito: str | None = None
    nome: str
    nome_canonico: str
    definicao: str | None = None
    aliases: list[str] | None = None


class ConceptResponse(ConceptCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


# ── ConceptRelation ───────────────────────────────────────────────────────────
class ConceptRelationCreate(BaseModel):
    concept_origem_id: str
    concept_destino_id: str
    dominio_origem: str = Field(..., pattern="^(fisiologia|treino|nutricao)$")
    dominio_destino: str = Field(..., pattern="^(fisiologia|treino|nutricao)$")
    tipo_relacao: str = Field(
        ...,
        pattern="^(influencia|requer|contraindica|melhora|correlaciona|componente_de|compensa)$"
    )
    forca: float | None = Field(None, ge=0.0, le=1.0)
    direcional: bool = True
    fonte_id: str | None = None


class ConceptRelationResponse(ConceptRelationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


# ── Busca vetorial ────────────────────────────────────────────────────────────
class SearchRequest(BaseModel):
    query: str
    dominio: str | None = Field(None, pattern="^(fisiologia|treino|nutricao)$")
    top_k: int = Field(5, ge=1, le=50)
    similarity_threshold: float = Field(0.0, ge=0.0, le=1.0)


class SearchResultItem(BaseModel):
    chunk_id: str
    source_id: str
    dominio: str
    conteudo: str
    score: float
    metadata: dict[str, Any] | None = None


class SearchResponse(BaseModel):
    query: str
    dominio: str | None
    results: list[SearchResultItem]
    total: int


# ── L2 Especialização ─────────────────────────────────────────────────────────
class FisiologiaMarcadorCreate(BaseModel):
    concept_id: str
    unidade: str | None = None
    categoria: str | None = Field(
        None,
        pattern="^(antropometrico|cardiovascular|metabolico|composicao_corporal)$"
    )
    faixa_ref_min: float | None = None
    faixa_ref_max: float | None = None
    estratificacao: dict[str, Any] | None = None


class TreinoExercicioCreate(BaseModel):
    concept_id: str
    padrao_movimento: str | None = None
    grupo_muscular_primario: list[str] | None = None
    grupo_muscular_secundario: list[str] | None = None
    equipamento: str | None = None
    tipo: str | None = None
    nivel: str | None = None


class TreinoProtocoloCreate(BaseModel):
    nome: str
    objetivo: str | None = None
    variaveis: dict[str, Any] | None = None


class TreinoProtocoloResponse(TreinoProtocoloCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


class NutricaoAlimentoCreate(BaseModel):
    concept_id: str
    categoria: str | None = None
    kcal_por_100g: float | None = None
    macros: dict[str, Any] | None = None
    micronutrientes: dict[str, Any] | None = None


class NutricaoProtocoloCreate(BaseModel):
    nome: str
    objetivo: str | None = None
    restricoes: dict[str, Any] | None = None


class NutricaoProtocoloResponse(NutricaoProtocoloCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
