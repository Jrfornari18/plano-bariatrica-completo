"""
models.py — Modelos Pydantic v2 para a API BodyScan KB.

Contratos de entrada/saída conforme seção 9 do PRD.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Entrada: POST /v1/recomendacoes
# -------------------------------------------------------------------------
class MetricaInput(BaseModel):
    """Métrica do BodyScan (IMC, RCQ, RCA, etc.)."""
    biomarcador: str = Field(..., description="Slug do biomarcador (ex: 'rca', 'imc')")
    valor: float = Field(..., description="Valor numérico da métrica")


class RecomendacaoRequest(BaseModel):
    """Requisição de recomendação por IA Generativa."""
    pseudonimo: str = Field(..., description="Pseudônimo do usuário (nunca PII direta)")
    contexto_clinico: str | None = Field(
        None,
        description="Slug do contexto clínico (ex: 'pos_rygb_0_12m', 'uso_glp1')",
    )
    metricas: list[MetricaInput] | None = Field(
        None,
        description="Métricas do BodyScan (IMC, RCQ, RCA, composição corporal)",
    )
    pergunta: str = Field(
        ...,
        description="Pergunta ou contexto do usuário",
        min_length=3,
        max_length=2000,
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "pseudonimo": "usr_abc123",
                "contexto_clinico": "perda_acelerada",
                "metricas": [
                    {"biomarcador": "rca", "valor": 0.6},
                    {"biomarcador": "imc", "valor": 28.5},
                ],
                "pergunta": "Como posso cuidar da pele durante a perda de peso?",
            }
        }
    }


# -------------------------------------------------------------------------
# Saída: POST /v1/recomendacoes
# -------------------------------------------------------------------------
class RecomendacaoResponse(BaseModel):
    """Resposta de recomendação ancorada em RAG."""
    escalonar: bool = Field(False, description="Indica se houve escalonamento")
    recomendacoes: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Recomendações elegíveis para o contexto",
    )
    chunks: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Chunks recuperados da base de conhecimento",
    )
    fontes: list[str] = Field(
        default_factory=list,
        description="Fontes citadas na resposta",
    )
    resposta_llm: str | None = Field(
        None,
        description="Resposta gerada pela LLM, ancorada nos chunks",
    )
    log_id: str | None = Field(None, description="ID do log de auditoria")
    aviso: str | None = Field(None, description="Aviso ou disclaimer")


class RespostaEscalonamento(BaseModel):
    """Resposta de desvio para profissional (gate de escalonamento)."""
    escalonar: bool = Field(True)
    tipo_alerta: str | None = Field(None, description="Tipo do alerta detectado")
    acao: str | None = Field(None, description="Ação recomendada")
    mensagem: str = Field(
        "Por favor, consulte um profissional de saúde habilitado.",
        description="Mensagem de orientação ao usuário",
    )


# -------------------------------------------------------------------------
# Entrada/Saída: POST /v1/ingestao/documento
# -------------------------------------------------------------------------
class IngestaoRequest(BaseModel):
    """Requisição de ingestão de documento."""
    documento_id: str = Field(..., description="UUID do documento a ingerir")


class IngestaoResponse(BaseModel):
    """Resposta de ingestão de documento."""
    documento_id: str
    chunks_gerados: int
    status: str


# -------------------------------------------------------------------------
# Entrada/Saída: POST /v1/feedback
# -------------------------------------------------------------------------
class FeedbackRequest(BaseModel):
    """Requisição de feedback sobre uma recomendação."""
    log_id: str = Field(..., description="ID do log de recomendação")
    util: bool | None = Field(None, description="A recomendação foi útil?")
    comentario: str | None = Field(None, description="Comentário opcional")

    model_config = {
        "json_schema_extra": {
            "example": {
                "log_id": "uuid-do-log",
                "util": True,
                "comentario": "Informação clara e útil.",
            }
        }
    }


class FeedbackResponse(BaseModel):
    """Resposta de registro de feedback."""
    ok: bool
