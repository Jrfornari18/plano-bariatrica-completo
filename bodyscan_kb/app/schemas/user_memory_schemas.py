"""
Schemas Pydantic v2 — Usuário (L3), Memória (L4) e Assistente (L5).
"""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ── Usuario (L3) ──────────────────────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    sexo_biologico: str | None = None
    data_nascimento: date | None = None
    altura_cm: int | None = None
    objetivo_principal: str | None = Field(
        None,
        pattern="^(emagrecimento|hipertrofia|performance|saude|reabilitacao)$"
    )
    nivel_atividade: str | None = None
    restricoes: dict[str, Any] | None = None


class UsuarioResponse(UsuarioCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


# ── PerfilFisiologicoSnapshot (L3) ────────────────────────────────────────────
class SnapshotCreate(BaseModel):
    scan_id: str | None = None
    data_medicao: datetime
    peso_kg: float | None = None
    imc: float | None = None
    circ_cintura: float | None = None
    circ_quadril: float | None = None
    circ_ombro: float | None = None
    rcq: float | None = None
    rca: float | None = None
    perc_gordura: float | None = None
    risco_cardiovascular: str | None = None
    fonte: str = Field("manual", pattern="^(bodyscan|manual|dispositivo)$")


class SnapshotResponse(SnapshotCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    usuario_id: str


# ── MemoriaEpisodica (L4) ─────────────────────────────────────────────────────
class EpisodioCreate(BaseModel):
    tipo_evento: str = Field(
        ...,
        pattern="^(scan_corporal|treino_realizado|refeicao_registrada|interacao_assistente|meta_definida|medicao)$"
    )
    dominio: str = Field(..., pattern="^(fisiologia|treino|nutricao|transversal)$")
    ref_entidade_tipo: str | None = None
    ref_entidade_id: str | None = None
    payload: dict[str, Any] | None = None
    ocorrido_em: datetime | None = None


class EpisodioResponse(EpisodioCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    usuario_id: str


# ── MemoriaSemantica (L4) ─────────────────────────────────────────────────────
class SemanticaCreate(BaseModel):
    dominio: str = Field(..., pattern="^(fisiologia|treino|nutricao|transversal)$")
    tipo: str = Field(
        ...,
        pattern="^(preferencia|restricao|padrao_comportamental|meta|insight_derivado)$"
    )
    afirmacao: str
    confianca: float | None = Field(None, ge=0.0, le=1.0)
    evidencia_episodios: list[str] | None = None
    valido_de: datetime | None = None
    valido_ate: datetime | None = None
    ativo: bool = True


class SemanticaResponse(SemanticaCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    usuario_id: str
    created_at: datetime


# ── MemoriaVinculoCrossDominio (L4) ───────────────────────────────────────────
class VinculoCrossCreate(BaseModel):
    conceito_fisiologia_id: str | None = None
    conceito_treino_id: str | None = None
    conceito_nutricao_id: str | None = None
    tipo_vinculo: str = Field(
        ...,
        pattern="^(causa_efeito|sinergia|conflito|dependencia|compensacao)$"
    )
    descricao: str | None = None
    forca: float | None = Field(None, ge=0.0, le=1.0)
    gerado_por: str = Field(
        "manual",
        pattern="^(regra|llm|analise_estatistica|manual)$"
    )
    evidencia: dict[str, Any] | None = None


class VinculoCrossResponse(VinculoCrossCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    usuario_id: str
    status: str
    created_at: datetime


# ── Assistente / Recuperação (L5) ─────────────────────────────────────────────
class RetrieveRequest(BaseModel):
    query: str
    dominios: list[str] | None = None
    top_k: int = Field(5, ge=1, le=20)
    incluir_memoria: bool = True
    incluir_cross_dominio: bool = True


class RetrieveContextItem(BaseModel):
    tipo: str  # "chunk" | "memoria_semantica" | "vinculo_cross"
    dominio: str
    conteudo: str
    score: float | None = None
    id: str


class RetrieveResponse(BaseModel):
    query: str
    snapshot_recente: SnapshotResponse | None
    contexto: list[RetrieveContextItem]
    memorias_aplicadas: list[dict[str, Any]]
    vinculos_validados: list[dict[str, Any]]
    log_id: str


# ── Feedback ──────────────────────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    log_id: str
    feedback: str = Field(..., pattern="^(positivo|negativo|neutro)$")


# ── Erro padrão ───────────────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
