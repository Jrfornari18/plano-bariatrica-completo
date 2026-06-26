"""
L1 — Conhecimento de domínio (camada canônica, read-mostly).
Entidades: knowledge_source, knowledge_chunk, concept, concept_relation.
"""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.core.database import Base


# ── Tipo JSON portável (SQLite usa JSON nativo, Postgres usa JSONB) ────────────
class JSONType(TypeDecorator):
    """Tipo JSON compatível com SQLite e PostgreSQL."""
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        return value


# ── Tipo Vector simplificado para SQLite MVP ──────────────────────────────────
class VectorType(TypeDecorator):
    """
    Armazena embeddings como JSON array no SQLite (MVP).
    Em produção com pgvector, substituir por sqlalchemy-pgvector Vector(N).
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        import json
        if isinstance(value, (list, tuple)):
            return json.dumps(value)
        return value

    def process_result_value(self, value: Any, dialect: Any) -> Any:
        if value is None:
            return None
        import json
        if isinstance(value, str):
            return json.loads(value)
        return value


def new_uuid() -> str:
    return str(uuid.uuid4())


# ── knowledge_source ──────────────────────────────────────────────────────────
class KnowledgeSource(Base):
    """Documento/fonte canônica de conhecimento de domínio."""
    __tablename__ = "knowledge_source"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    dominio: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="fisiologia | treino | nutricao"
    )
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="paper | livro | protocolo | diretriz | nota_interna"
    )
    autor: Mapped[str | None] = mapped_column(Text)
    referencia: Mapped[str | None] = mapped_column(Text, comment="DOI/URL/ISBN")
    ano: Mapped[int | None] = mapped_column(Integer)
    confiabilidade: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="primaria | oficial | secundaria"
    )
    idioma: Mapped[str | None] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    concept_relations: Mapped[list["ConceptRelation"]] = relationship(
        back_populates="fonte", foreign_keys="ConceptRelation.fonte_id"
    )

    __table_args__ = (
        CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao')",
            name="ck_ks_dominio"
        ),
        CheckConstraint(
            "confiabilidade IN ('primaria','oficial','secundaria')",
            name="ck_ks_confiabilidade"
        ),
        CheckConstraint(
            "tipo IN ('paper','livro','protocolo','diretriz','nota_interna')",
            name="ck_ks_tipo"
        ),
    )


# ── knowledge_chunk ───────────────────────────────────────────────────────────
class KnowledgeChunk(Base):
    """Trecho vetorizado — unidade de recuperação RAG."""
    __tablename__ = "knowledge_chunk"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_source.id", ondelete="CASCADE"),
        nullable=False
    )
    dominio: Mapped[str] = mapped_column(
        String(20), nullable=False,
        comment="Desnormalizado para filtro rápido por base"
    )
    ordem: Mapped[int | None] = mapped_column(Integer, comment="Posição no documento")
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    tokens: Mapped[int | None] = mapped_column(Integer)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType, comment="Vetor de embedding (JSON no SQLite, vector(N) no Postgres)"
    )
    embedding_model_version: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Permite reindexação controlada"
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONType, default=dict, comment="Seção, página, tags"
    )

    # Relacionamentos
    source: Mapped["KnowledgeSource"] = relationship(back_populates="chunks")

    __table_args__ = (
        CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao')",
            name="ck_kc_dominio"
        ),
    )


# ── concept ───────────────────────────────────────────────────────────────────
class Concept(Base):
    """Nó da ontologia — entidade de conhecimento estruturado."""
    __tablename__ = "concept"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    dominio: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_conceito: Mapped[str | None] = mapped_column(
        String(50), comment="marcador | exercicio | alimento | protocolo"
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    nome_canonico: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="slug único por domínio"
    )
    definicao: Mapped[str | None] = mapped_column(Text)
    aliases: Mapped[list | None] = mapped_column(JSONType, default=list)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType, comment="Opcional — busca semântica de conceitos"
    )

    # Relacionamentos
    relations_origem: Mapped[list["ConceptRelation"]] = relationship(
        back_populates="concept_origem",
        foreign_keys="ConceptRelation.concept_origem_id",
        cascade="all, delete-orphan",
    )
    relations_destino: Mapped[list["ConceptRelation"]] = relationship(
        back_populates="concept_destino",
        foreign_keys="ConceptRelation.concept_destino_id",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("dominio", "nome_canonico", name="uq_concept_dominio_nome"),
        CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao')",
            name="ck_concept_dominio"
        ),
    )


# ── concept_relation ──────────────────────────────────────────────────────────
class ConceptRelation(Base):
    """
    Aresta do grafo de conceitos.
    Suporta relações intra-domínio e cross-domínio (dominio_origem ≠ dominio_destino).
    """
    __tablename__ = "concept_relation"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=new_uuid
    )
    concept_origem_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concept.id", ondelete="CASCADE"), nullable=False
    )
    concept_destino_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("concept.id", ondelete="CASCADE"), nullable=False
    )
    dominio_origem: Mapped[str] = mapped_column(String(20), nullable=False)
    dominio_destino: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_relacao: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="influencia | requer | contraindica | melhora | correlaciona | componente_de | compensa"
    )
    forca: Mapped[float | None] = mapped_column(
        Float, comment="0.0 a 1.0"
    )
    direcional: Mapped[bool] = mapped_column(Boolean, default=True)
    fonte_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("knowledge_source.id"), nullable=True
    )

    # Relacionamentos
    concept_origem: Mapped["Concept"] = relationship(
        back_populates="relations_origem",
        foreign_keys=[concept_origem_id],
    )
    concept_destino: Mapped["Concept"] = relationship(
        back_populates="relations_destino",
        foreign_keys=[concept_destino_id],
    )
    fonte: Mapped["KnowledgeSource | None"] = relationship(
        back_populates="concept_relations",
        foreign_keys=[fonte_id],
    )

    __table_args__ = (
        CheckConstraint(
            "concept_origem_id <> concept_destino_id",
            name="ck_cr_no_self_loop"
        ),
        CheckConstraint(
            "dominio_origem IN ('fisiologia','treino','nutricao')",
            name="ck_cr_dominio_origem"
        ),
        CheckConstraint(
            "dominio_destino IN ('fisiologia','treino','nutricao')",
            name="ck_cr_dominio_destino"
        ),
        CheckConstraint(
            "tipo_relacao IN ('influencia','requer','contraindica','melhora','correlaciona','componente_de','compensa')",
            name="ck_cr_tipo_relacao"
        ),
    )
