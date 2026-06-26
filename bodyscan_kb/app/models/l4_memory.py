"""
L4 — Memória.
Entidades: memoria_episodica, memoria_semantica,
           memoria_vinculo_cross_dominio, contexto_sessao.
Dados derivados e temporais — sensíveis (LGPD).
"""
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.core.database import Base
from app.models.l1_knowledge import VectorType, new_uuid


class JSONType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        return value


# ── memoria_episodica ─────────────────────────────────────────────────────────
class MemoriaEpisodica(Base):
    """
    Linha do tempo unificada dos três domínios.
    Cada evento é imutável após criação.
    """
    __tablename__ = "memoria_episodica"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    tipo_evento: Mapped[str] = mapped_column(
        String(40), nullable=False,
        comment="scan_corporal | treino_realizado | refeicao_registrada | interacao_assistente | meta_definida | medicao"
    )
    dominio: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="fisiologia | treino | nutricao | transversal"
    )
    ref_entidade_tipo: Mapped[str | None] = mapped_column(
        String(50), comment="Tipo da entidade de origem (polimórfico)"
    )
    ref_entidade_id: Mapped[str | None] = mapped_column(
        String(36), comment="ID da entidade de origem"
    )
    payload: Mapped[dict | None] = mapped_column(
        JSONType, default=dict, comment="Snapshot do evento — sem PII explícito"
    )
    ocorrido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    usuario: Mapped["app.models.l3_subject.Usuario"] = relationship(
        foreign_keys=[usuario_id]
    )

    __table_args__ = (
        CheckConstraint(
            "tipo_evento IN ('scan_corporal','treino_realizado','refeicao_registrada','interacao_assistente','meta_definida','medicao')",
            name="ck_me_tipo_evento"
        ),
        CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao','transversal')",
            name="ck_me_dominio"
        ),
    )


# ── memoria_semantica ─────────────────────────────────────────────────────────
class MemoriaSemantica(Base):
    """
    Fatos e preferências de longo prazo aprendidos sobre o usuário.
    Suporta validade temporal (fatos expiram).
    """
    __tablename__ = "memoria_semantica"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    dominio: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="fisiologia | treino | nutricao | transversal"
    )
    tipo: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="preferencia | restricao | padrao_comportamental | meta | insight_derivado"
    )
    afirmacao: Mapped[str] = mapped_column(
        Text, nullable=False,
        comment="Ex.: 'responde bem a treino de força 3x/semana'"
    )
    confianca: Mapped[float | None] = mapped_column(
        Float, comment="0.0 a 1.0"
    )
    evidencia_episodios: Mapped[dict | None] = mapped_column(
        JSONType, default=list,
        comment="IDs de memoria_episodica que sustentam o fato"
    )
    valido_de: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valido_ate: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType, comment="Para recuperação semântica"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["app.models.l3_subject.Usuario"] = relationship(
        foreign_keys=[usuario_id]
    )

    __table_args__ = (
        CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao','transversal')",
            name="ck_ms_dominio"
        ),
        CheckConstraint(
            "tipo IN ('preferencia','restricao','padrao_comportamental','meta','insight_derivado')",
            name="ck_ms_tipo"
        ),
        CheckConstraint(
            "confianca BETWEEN 0.0 AND 1.0 OR confianca IS NULL",
            name="ck_ms_confianca"
        ),
    )


# ── memoria_vinculo_cross_dominio ─────────────────────────────────────────────
class MemoriaVinculoCrossDominio(Base):
    """
    Núcleo da memória entre as três bases.
    Exige ≥ 2 domínios preenchidos.
    Status inicia sempre em 'hipotese' — nunca 'validado' automaticamente.
    """
    __tablename__ = "memoria_vinculo_cross_dominio"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    conceito_fisiologia_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("concept.id"), nullable=True
    )
    conceito_treino_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("concept.id"), nullable=True
    )
    conceito_nutricao_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("concept.id"), nullable=True
    )
    tipo_vinculo: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="causa_efeito | sinergia | conflito | dependencia | compensacao"
    )
    descricao: Mapped[str | None] = mapped_column(
        Text,
        comment="Ex.: 'RCA elevada + protocolo hipercalórico ⇒ priorizar cardio'"
    )
    forca: Mapped[float | None] = mapped_column(Float, comment="0.0 a 1.0")
    gerado_por: Mapped[str] = mapped_column(
        String(20), nullable=False, default="manual",
        comment="regra | llm | analise_estatistica | manual"
    )
    evidencia: Mapped[dict | None] = mapped_column(
        JSONType, default=dict,
        comment="Episódios/snapshots de suporte"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="hipotese",
        comment="hipotese | validado | refutado — nunca 'validado' automaticamente"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["app.models.l3_subject.Usuario"] = relationship(
        foreign_keys=[usuario_id]
    )

    __table_args__ = (
        CheckConstraint(
            "tipo_vinculo IN ('causa_efeito','sinergia','conflito','dependencia','compensacao')",
            name="ck_mvcd_tipo"
        ),
        CheckConstraint(
            "status IN ('hipotese','validado','refutado')",
            name="ck_mvcd_status"
        ),
        CheckConstraint(
            "gerado_por IN ('regra','llm','analise_estatistica','manual')",
            name="ck_mvcd_gerado_por"
        ),
        # Constraint: pelo menos 2 domínios preenchidos (RF-D3)
        CheckConstraint(
            "(CASE WHEN conceito_fisiologia_id IS NOT NULL THEN 1 ELSE 0 END + "
            " CASE WHEN conceito_treino_id IS NOT NULL THEN 1 ELSE 0 END + "
            " CASE WHEN conceito_nutricao_id IS NOT NULL THEN 1 ELSE 0 END) >= 2",
            name="ck_mvcd_min_2_dominios"
        ),
    )


# ── contexto_sessao ───────────────────────────────────────────────────────────
class ContextoSessao(Base):
    """
    Memória de trabalho (curto prazo) do assistente.
    Expira automaticamente após TTL configurado.
    """
    __tablename__ = "contexto_sessao"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    usuario_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    sessao_id: Mapped[str] = mapped_column(
        String(36), nullable=False, comment="Identificador externo da sessão"
    )
    janela_contexto: Mapped[dict | None] = mapped_column(
        JSONType, default=dict,
        comment="chunks recuperados + memórias ativas — sem PII"
    )
    objetivo_sessao: Mapped[str | None] = mapped_column(Text)
    expira_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    usuario: Mapped["app.models.l3_subject.Usuario"] = relationship(
        foreign_keys=[usuario_id]
    )
