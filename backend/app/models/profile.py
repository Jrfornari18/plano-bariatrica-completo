"""
Schemas Pydantic v2 para perfis de usuário (RF-07).
Integra métricas do BodyScan (IMC, RCQ, RCA).
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProfileCreate(BaseModel):
    apelido: Optional[str] = None
    idade: Optional[int] = Field(None, ge=10, le=100)
    sexo: Optional[str] = Field(None, pattern="^(M|F|outro)$")
    altura_cm: Optional[float] = Field(None, ge=100, le=250)
    peso_kg: Optional[float] = Field(None, ge=20, le=300)
    # Métricas do BodyScan
    imc: Optional[float] = Field(None, ge=10, le=60)
    rcq: Optional[float] = Field(None, ge=0.5, le=1.5)
    rca: Optional[float] = Field(None, ge=0.2, le=1.0)
    # Preferências
    nivel_experiencia: Optional[str] = Field(
        None, pattern="^(iniciante|intermediario|avancado)$"
    )
    objetivo_id: Optional[int] = None
    frequencia_semanal: Optional[int] = Field(None, ge=1, le=7)
    local_preferido: Optional[str] = None
    restricoes: Optional[str] = None
    equipamentos_disponiveis: Optional[str] = None


class ProfileResponse(ProfileCreate):
    id: int
    criado_em: Optional[str] = None

    model_config = {"from_attributes": True}
