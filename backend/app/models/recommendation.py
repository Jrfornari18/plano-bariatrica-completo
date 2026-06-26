"""
Schemas Pydantic v2 para o motor de recomendação (RF-05, schema 8.2 do PRD).
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


# ─── Itens do treino gerado ───────────────────────────────────────────────────

class TrainingItem(BaseModel):
    exercicio_id: int
    nome: str
    series: int = Field(ge=1)
    repeticoes: str  # pode ser "12" ou "40s"
    descanso_seg: int = Field(ge=0)
    alternativa: Optional[str] = None
    regressao: Optional[str] = None
    progressao: Optional[str] = None


class TrainingBlock(BaseModel):
    bloco: str  # aquecimento | principal | finalizacao
    itens: List[TrainingItem]


class TrainingPlan(BaseModel):
    nome: str
    modalidade: str
    objetivo: str
    nivel: str
    duracao_min: int
    estrutura: str
    blocos: List[TrainingBlock]


# ─── Request / Response ───────────────────────────────────────────────────────

class RecommendationRequest(BaseModel):
    perfil_id: Optional[int] = None
    # Perfil inline (alternativa ao perfil_id)
    nivel: Optional[str] = Field(None, pattern="^(iniciante|intermediario|avancado)$")
    intencao: str = Field(..., min_length=5, max_length=500)
    modalidades: Optional[List[str]] = None
    duracao_min: Optional[int] = Field(None, ge=10, le=120)
    local: Optional[str] = None
    equipamentos_disponiveis: Optional[List[str]] = None
    restricoes: Optional[List[str]] = None
    top_k: int = Field(default=8, ge=1, le=20)

    @field_validator("modalidades", mode="before")
    @classmethod
    def normalise_modalidades(cls, v):
        if v is None:
            return v
        allowed = {"funcional", "calistenia", "musculacao", "aerobico", "esportes"}
        normalised = []
        for m in v:
            m_lower = m.lower().replace("ç", "c").replace("ã", "a")
            normalised.append(m_lower)
        return normalised


class RecommendationResponse(BaseModel):
    recomendacao_id: int
    degraded: bool = False
    treino: TrainingPlan
    justificativa: str
    contexto_recuperado: List[int]


class FeedbackRequest(BaseModel):
    nota: int = Field(..., ge=1, le=5)

    @field_validator("nota")
    @classmethod
    def validate_nota(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Nota deve estar entre 1 e 5")
        return v


class FeedbackResponse(BaseModel):
    recomendacao_id: int
    nota: int
    mensagem: str = "Feedback registrado com sucesso"
