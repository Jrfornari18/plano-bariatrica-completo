"""
schemas.py — Modelos Pydantic v2 para contratos de API.

Contratos conforme seção 9 do PRD:
  POST /v1/recomendacoes
  POST /v1/ingestao/documento
  GET  /v1/conhecimento/buscar
  POST /v1/feedback
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator


# -------------------------------------------------------------------------
# Modelos de entrada
# -------------------------------------------------------------------------

class MetricaInput(BaseModel):
    """Biomarcador + valor do BodyScan."""
    biomarcador: str = Field(..., description="Slug do biomarcador (ex.: 'imc', 'rca')")
    valor: float = Field(..., description="Valor numérico da métrica")


class RecomendacaoRequest(BaseModel):
    """
    POST /v1/recomendacoes

    Entrada: perfil pseudonimizado + contexto clínico + métricas + pergunta.
    """
    pseudonimo: str = Field(..., description="Identificador pseudonimizado do usuário")
    contexto_clinico: str | None = Field(
        default=None,
        description="Slug do contexto clínico (ex.: 'pos_bariatrico_rygb')",
    )
    metricas: list[MetricaInput] = Field(
        default_factory=list,
        description="Métricas do BodyScan (IMC, RCQ, RCA, etc.)",
    )
    pergunta: str = Field(..., min_length=3, description="Pergunta ou intenção do usuário")
    incluir_supervisao: bool = Field(
        default=False,
        description="Se True, inclui conteúdo que exige supervisão médica (apenas para profissionais)",
    )
    k: int = Field(default=6, ge=1, le=20, description="Número máximo de chunks a recuperar")


class IngestaoDocumentoRequest(BaseModel):
    """POST /v1/ingestao/documento"""
    documento_id: str = Field(..., description="UUID do documento_conhecimento a ingerir")


class BuscarRequest(BaseModel):
    """GET /v1/conhecimento/buscar (parâmetros de query)"""
    q: str = Field(..., description="Consulta de busca")
    contextos: list[str] | None = Field(default=None, description="Filtro de contextos clínicos")
    k: int = Field(default=6, ge=1, le=20)
    incluir_supervisao: bool = Field(default=False)


class FeedbackRequest(BaseModel):
    """POST /v1/feedback"""
    log_id: str = Field(..., description="UUID do log_recomendacao")
    util: bool | None = Field(default=None, description="Recomendação foi útil?")
    comentario: str | None = Field(default=None, description="Comentário opcional")


# -------------------------------------------------------------------------
# Modelos de saída
# -------------------------------------------------------------------------

class EscalonamentoResponse(BaseModel):
    """Resposta de desvio para profissional (gate de escalonamento)."""
    escalonar: bool = True
    tipo_alerta: str
    acao: str
    mensagem: str = (
        "Esta pergunta requer orientação de um profissional de saúde habilitado. "
        "Por favor, consulte seu médico ou nutricionista."
    )


class ChunkResponse(BaseModel):
    """Chunk recuperado da base de conhecimento."""
    id: str
    texto: str
    distancia: float
    requer_supervisao: bool
    dominio_slug: str | None = None
    contexto_slugs: list[str] = Field(default_factory=list)
    nivel_evidencia: str = "fisiologia_estabelecida"


class RecomendacaoItem(BaseModel):
    """Item de recomendação elegível."""
    slug: str
    titulo: str
    forca: str
    requer_supervisao: bool


class RecomendacaoResponse(BaseModel):
    """
    Resposta de POST /v1/recomendacoes (fluxo normal, sem escalonamento).

    Grounding obrigatório: resposta ancorada apenas nos chunks recuperados.
    Fontes citadas obrigatoriamente.
    """
    escalonar: bool = False
    resposta: str = Field(..., description="Resposta gerada pela LLM com grounding")
    recomendacoes: list[RecomendacaoItem] = Field(default_factory=list)
    chunks: list[ChunkResponse] = Field(default_factory=list)
    fontes: list[str] = Field(default_factory=list)
    log_id: str = Field(..., description="UUID do log_recomendacao para auditoria")
    aviso: str = (
        "Esta informação é educativa e não substitui avaliação médica ou nutricional. "
        "Consulte um profissional de saúde habilitado."
    )


class NaoCobertoResponse(BaseModel):
    """Resposta quando a KB não cobre o tema (RF-12)."""
    escalonar: bool = False
    coberto: bool = False
    mensagem: str = (
        "Não encontrei informações suficientes na base de conhecimento para responder "
        "a esta pergunta com segurança. Por favor, consulte um profissional de saúde."
    )
    log_id: str


class IngestaoResponse(BaseModel):
    """Resposta de POST /v1/ingestao/documento"""
    documento_id: str
    chunks_gerados: int


class BuscarResponse(BaseModel):
    """Resposta de GET /v1/conhecimento/buscar"""
    chunks: list[ChunkResponse]
    total: int


class FeedbackResponse(BaseModel):
    """Resposta de POST /v1/feedback"""
    ok: bool = True
    feedback_id: str
