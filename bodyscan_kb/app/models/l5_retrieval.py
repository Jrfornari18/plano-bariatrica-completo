"""
L5 — Recuperação e observabilidade.
Entidade: recuperacao_log.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    ForeignKey,
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


class RecuperacaoLog(Base):
    """
    Log de observabilidade do RAG.
    Registra query, domínios consultados, chunks recuperados,
    memórias aplicadas, resposta gerada e feedback.
    Sem PII — apenas IDs e scores (RNF-4).
    """
    __tablename__ = "recuperacao_log"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    dominios_consultados: Mapped[dict | None] = mapped_column(
        JSONType, default=list, comment="Lista de domínios consultados"
    )
    chunks_recuperados: Mapped[dict | None] = mapped_column(
        JSONType, default=list,
        comment="[{chunk_id, score, dominio}] — sem conteúdo completo"
    )
    memorias_aplicadas: Mapped[dict | None] = mapped_column(
        JSONType, default=list,
        comment="[{memoria_id, tipo, dominio}] — sem afirmações completas"
    )
    resposta_gerada: Mapped[str | None] = mapped_column(
        Text, comment="Resumo da resposta (sem PII)"
    )
    feedback: Mapped[str | None] = mapped_column(
        String(20), comment="positivo | negativo | neutro"
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["app.models.l3_subject.Usuario"] = relationship(
        foreign_keys=[usuario_id]
    )
