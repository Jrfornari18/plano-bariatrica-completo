"""
L3 — Sujeito.
Entidades: usuario, perfil_fisiologico_snapshot.
Dados sensíveis (LGPD) — nenhum PII deve aparecer em logs.
"""
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.core.database import Base
from app.models.l1_knowledge import new_uuid


class JSONType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        return value


# ── usuario ───────────────────────────────────────────────────────────────────
class Usuario(Base):
    """
    Identidade e perfil do usuário.
    Dados sensíveis — tratamento conforme LGPD.
    """
    __tablename__ = "usuario"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    sexo_biologico: Mapped[str | None] = mapped_column(
        String(10), comment="M | F | outro"
    )
    data_nascimento: Mapped[date | None] = mapped_column(Date)
    altura_cm: Mapped[int | None] = mapped_column(Integer)
    objetivo_principal: Mapped[str | None] = mapped_column(
        String(30),
        comment="emagrecimento | hipertrofia | performance | saude | reabilitacao"
    )
    nivel_atividade: Mapped[str | None] = mapped_column(
        String(20),
        comment="sedentario | leve | moderado | intenso | muito_intenso"
    )
    restricoes: Mapped[dict | None] = mapped_column(
        JSONType, default=dict,
        comment="lesões, alergias, condições médicas — dado sensível"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    snapshots: Mapped[list["PerfilFisiologicoSnapshot"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "objetivo_principal IN ('emagrecimento','hipertrofia','performance','saude','reabilitacao') OR objetivo_principal IS NULL",
            name="ck_usuario_objetivo"
        ),
    )


# ── perfil_fisiologico_snapshot ───────────────────────────────────────────────
class PerfilFisiologicoSnapshot(Base):
    """
    Snapshot imutável e versionado por data do perfil fisiológico.
    Ponte com o BodyScan via scan_id.
    Habilita séries temporais e correlação com eventos de treino/nutrição.
    """
    __tablename__ = "perfil_fisiologico_snapshot"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    scan_id: Mapped[str | None] = mapped_column(
        String(36), nullable=True,
        comment="Referência ao scan do BodyScan (nullable para entrada manual)"
    )
    data_medicao: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    peso_kg: Mapped[float | None] = mapped_column(Float)
    imc: Mapped[float | None] = mapped_column(Float)
    circ_cintura: Mapped[float | None] = mapped_column(Float, comment="cm")
    circ_quadril: Mapped[float | None] = mapped_column(Float, comment="cm")
    circ_ombro: Mapped[float | None] = mapped_column(Float, comment="cm")
    rcq: Mapped[float | None] = mapped_column(Float, comment="Relação cintura-quadril")
    rca: Mapped[float | None] = mapped_column(Float, comment="Relação cintura-altura")
    perc_gordura: Mapped[float | None] = mapped_column(Float, comment="%")
    risco_cardiovascular: Mapped[str | None] = mapped_column(
        String(20), comment="baixo | moderado | alto | muito_alto"
    )
    fonte: Mapped[str] = mapped_column(
        String(20), nullable=False, default="manual",
        comment="bodyscan | manual | dispositivo"
    )

    # Relacionamentos
    usuario: Mapped["Usuario"] = relationship(back_populates="snapshots")

    __table_args__ = (
        CheckConstraint(
            "fonte IN ('bodyscan','manual','dispositivo')",
            name="ck_pfs_fonte"
        ),
        # Índice para série temporal por usuário (PRD seção 10)
        Index("idx_pfs_usuario_data", "usuario_id", "data_medicao"),
    )
