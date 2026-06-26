"""
Schemas Pydantic v2 para exercícios (RF-08).
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class ExerciseBase(BaseModel):
    id: int
    nome: str
    slug: str
    modalidade: str
    nivel_dificuldade: str
    descricao: str
    met: Optional[float] = None
    composto: Optional[int] = None
    contraindicacoes: Optional[str] = None
    exercicio_regressao_id: Optional[int] = None
    exercicio_progressao_id: Optional[int] = None


class ExerciseDetail(ExerciseBase):
    instrucoes_execucao: Optional[str] = None
    dicas_tecnica: Optional[str] = None
    erros_comuns: Optional[str] = None
    musculos: List[str] = Field(default_factory=list)
    equipamentos: List[str] = Field(default_factory=list)
    objetivos: List[str] = Field(default_factory=list)
    alternativas: List[int] = Field(default_factory=list)
    regressao_nome: Optional[str] = None
    progressao_nome: Optional[str] = None


class ExerciseListResponse(BaseModel):
    total: int
    exercicios: List[ExerciseDetail]


class ExerciseFilter(BaseModel):
    modalidade: Optional[str] = None
    nivel: Optional[str] = None
    objetivo: Optional[str] = None
    equipamento: Optional[str] = None
    local: Optional[str] = None  # casa | academia
