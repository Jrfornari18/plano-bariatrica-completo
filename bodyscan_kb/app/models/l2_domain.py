"""
L2 — Especialização de domínio.
Tabelas 1:1 com concept + tabelas de protocolo independentes.
"""
import uuid
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator
from typing import Any

from app.core.database import Base
from app.models.l1_knowledge import new_uuid


class JSONType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        return value


# ── fisiologia_marcador ───────────────────────────────────────────────────────
class FisiologiaMarcador(Base):
    """
    Especialização de concept para marcadores fisiológicos.
    Suporta IMC, RCQ, RCA, % gordura com faixas de referência estratificadas.
    """
    __tablename__ = "fisiologia_marcador"

    concept_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concept.id", ondelete="CASCADE"),
        primary_key=True
    )
    unidade: Mapped[str | None] = mapped_column(String(30), comment="kg/m², cm, %, etc.")
    categoria: Mapped[str | None] = mapped_column(
        String(30),
        comment="antropometrico | cardiovascular | metabolico | composicao_corporal"
    )
    faixa_ref_min: Mapped[float | None] = mapped_column(Float)
    faixa_ref_max: Mapped[float | None] = mapped_column(Float)
    estratificacao: Mapped[dict | None] = mapped_column(
        JSONType, default=dict,
        comment="Faixas por sexo/idade: {sexo: {faixa_etaria: {min, max, risco}}}"
    )

    # Relacionamento
    concept: Mapped["app.models.l1_knowledge.Concept"] = relationship(
        foreign_keys=[concept_id]
    )

    __table_args__ = (
        CheckConstraint(
            "categoria IN ('antropometrico','cardiovascular','metabolico','composicao_corporal')",
            name="ck_fm_categoria"
        ),
    )


# ── treino_exercicio ──────────────────────────────────────────────────────────
class TreinoExercicio(Base):
    """Especialização de concept para exercícios físicos."""
    __tablename__ = "treino_exercicio"

    concept_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concept.id", ondelete="CASCADE"),
        primary_key=True
    )
    padrao_movimento: Mapped[str | None] = mapped_column(
        String(30),
        comment="empurrar | puxar | agachar | dobrar_quadril | core | locomocao"
    )
    grupo_muscular_primario: Mapped[dict | None] = mapped_column(JSONType, default=list)
    grupo_muscular_secundario: Mapped[dict | None] = mapped_column(JSONType, default=list)
    equipamento: Mapped[str | None] = mapped_column(String(100))
    tipo: Mapped[str | None] = mapped_column(
        String(20),
        comment="forca | hipertrofia | resistencia | mobilidade | cardio"
    )
    nivel: Mapped[str | None] = mapped_column(
        String(20),
        comment="iniciante | intermediario | avancado"
    )

    concept: Mapped["app.models.l1_knowledge.Concept"] = relationship(
        foreign_keys=[concept_id]
    )

    __table_args__ = (
        CheckConstraint(
            "padrao_movimento IN ('empurrar','puxar','agachar','dobrar_quadril','core','locomocao') OR padrao_movimento IS NULL",
            name="ck_te_padrao"
        ),
        CheckConstraint(
            "tipo IN ('forca','hipertrofia','resistencia','mobilidade','cardio') OR tipo IS NULL",
            name="ck_te_tipo"
        ),
    )


# ── treino_protocolo ──────────────────────────────────────────────────────────
class TreinoProtocolo(Base):
    """Protocolo de treino (HIIT, 5x5, periodização linear, etc.)."""
    __tablename__ = "treino_protocolo"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    objetivo: Mapped[str | None] = mapped_column(Text)
    variaveis: Mapped[dict | None] = mapped_column(
        JSONType, default=dict,
        comment="séries, reps, intensidade, descanso, frequência"
    )


# ── nutricao_alimento ─────────────────────────────────────────────────────────
class NutricaoAlimento(Base):
    """Especialização de concept para alimentos."""
    __tablename__ = "nutricao_alimento"

    concept_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concept.id", ondelete="CASCADE"),
        primary_key=True
    )
    categoria: Mapped[str | None] = mapped_column(String(50))
    kcal_por_100g: Mapped[float | None] = mapped_column(Float)
    macros: Mapped[dict | None] = mapped_column(
        JSONType, default=dict,
        comment="{proteina_g, carboidrato_g, gordura_g, fibra_g}"
    )
    micronutrientes: Mapped[dict | None] = mapped_column(JSONType, default=dict)

    concept: Mapped["app.models.l1_knowledge.Concept"] = relationship(
        foreign_keys=[concept_id]
    )


# ── nutricao_protocolo ────────────────────────────────────────────────────────
class NutricaoProtocolo(Base):
    """Protocolo nutricional (low carb, jejum intermitente, etc.)."""
    __tablename__ = "nutricao_protocolo"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    objetivo: Mapped[str | None] = mapped_column(Text)
    restricoes: Mapped[dict | None] = mapped_column(
        JSONType, default=dict,
        comment="Restrições alimentares, janelas de alimentação, etc."
    )
