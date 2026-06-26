"""Esquema inicial — L1 a L5 (knowledge, domain, subject, memory, retrieval)

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-01 00:00:00.000000

CP-1: Schema e índices conferem com modelo_dados_kb_memoria.md
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── L1 — knowledge_source ─────────────────────────────────────────────────
    op.create_table(
        "knowledge_source",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dominio", sa.String(20), nullable=False),
        sa.Column("titulo", sa.Text, nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("autor", sa.Text),
        sa.Column("referencia", sa.Text),
        sa.Column("ano", sa.Integer),
        sa.Column("confiabilidade", sa.String(20), nullable=False),
        sa.Column("idioma", sa.String(2)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao')", name="ck_ks_dominio"
        ),
        sa.CheckConstraint(
            "confiabilidade IN ('primaria','oficial','secundaria')", name="ck_ks_confiabilidade"
        ),
        sa.CheckConstraint(
            "tipo IN ('paper','livro','protocolo','diretriz','nota_interna')", name="ck_ks_tipo"
        ),
    )

    # ── L1 — concept ──────────────────────────────────────────────────────────
    op.create_table(
        "concept",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("dominio", sa.String(20), nullable=False),
        sa.Column("tipo_conceito", sa.String(50)),
        sa.Column("nome", sa.Text, nullable=False),
        sa.Column("nome_canonico", sa.String(200), nullable=False),
        sa.Column("definicao", sa.Text),
        sa.Column("aliases", sa.JSON),
        sa.Column("embedding", sa.Text),
        sa.UniqueConstraint("dominio", "nome_canonico", name="uq_concept_dominio_nome"),
        sa.CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao')", name="ck_concept_dominio"
        ),
    )

    # ── L1 — knowledge_chunk ──────────────────────────────────────────────────
    op.create_table(
        "knowledge_chunk",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_id", sa.String(36), sa.ForeignKey("knowledge_source.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dominio", sa.String(20), nullable=False),
        sa.Column("ordem", sa.Integer),
        sa.Column("conteudo", sa.Text, nullable=False),
        sa.Column("tokens", sa.Integer),
        sa.Column("embedding", sa.Text),
        sa.Column("embedding_model_version", sa.String(50), nullable=False),
        sa.Column("metadata", sa.JSON),
        sa.CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao')", name="ck_kc_dominio"
        ),
    )
    op.create_index("idx_chunk_dominio", "knowledge_chunk", ["dominio"])

    # ── L1 — concept_relation ─────────────────────────────────────────────────
    op.create_table(
        "concept_relation",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("concept_origem_id", sa.String(36), sa.ForeignKey("concept.id", ondelete="CASCADE"), nullable=False),
        sa.Column("concept_destino_id", sa.String(36), sa.ForeignKey("concept.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dominio_origem", sa.String(20), nullable=False),
        sa.Column("dominio_destino", sa.String(20), nullable=False),
        sa.Column("tipo_relacao", sa.String(30), nullable=False),
        sa.Column("forca", sa.Float),
        sa.Column("direcional", sa.Boolean, server_default="1"),
        sa.Column("fonte_id", sa.String(36), sa.ForeignKey("knowledge_source.id")),
        sa.CheckConstraint("concept_origem_id <> concept_destino_id", name="ck_cr_no_self_loop"),
        sa.CheckConstraint("dominio_origem IN ('fisiologia','treino','nutricao')", name="ck_cr_dominio_origem"),
        sa.CheckConstraint("dominio_destino IN ('fisiologia','treino','nutricao')", name="ck_cr_dominio_destino"),
        sa.CheckConstraint(
            "tipo_relacao IN ('influencia','requer','contraindica','melhora','correlaciona','componente_de','compensa')",
            name="ck_cr_tipo_relacao"
        ),
    )
    # Índice para consultas cross-domínio (PRD seção 10)
    op.create_index("idx_cr_cross_domain", "concept_relation", ["dominio_origem", "dominio_destino"])

    # ── L2 — fisiologia_marcador ──────────────────────────────────────────────
    op.create_table(
        "fisiologia_marcador",
        sa.Column("concept_id", sa.String(36), sa.ForeignKey("concept.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("unidade", sa.String(30)),
        sa.Column("categoria", sa.String(30)),
        sa.Column("faixa_ref_min", sa.Float),
        sa.Column("faixa_ref_max", sa.Float),
        sa.Column("estratificacao", sa.JSON),
        sa.CheckConstraint(
            "categoria IN ('antropometrico','cardiovascular','metabolico','composicao_corporal')",
            name="ck_fm_categoria"
        ),
    )

    # ── L2 — treino_exercicio ─────────────────────────────────────────────────
    op.create_table(
        "treino_exercicio",
        sa.Column("concept_id", sa.String(36), sa.ForeignKey("concept.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("padrao_movimento", sa.String(30)),
        sa.Column("grupo_muscular_primario", sa.JSON),
        sa.Column("grupo_muscular_secundario", sa.JSON),
        sa.Column("equipamento", sa.String(100)),
        sa.Column("tipo", sa.String(20)),
        sa.Column("nivel", sa.String(20)),
    )

    # ── L2 — treino_protocolo ─────────────────────────────────────────────────
    op.create_table(
        "treino_protocolo",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(200), nullable=False, unique=True),
        sa.Column("objetivo", sa.Text),
        sa.Column("variaveis", sa.JSON),
    )

    # ── L2 — nutricao_alimento ────────────────────────────────────────────────
    op.create_table(
        "nutricao_alimento",
        sa.Column("concept_id", sa.String(36), sa.ForeignKey("concept.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("categoria", sa.String(50)),
        sa.Column("kcal_por_100g", sa.Float),
        sa.Column("macros", sa.JSON),
        sa.Column("micronutrientes", sa.JSON),
    )

    # ── L2 — nutricao_protocolo ───────────────────────────────────────────────
    op.create_table(
        "nutricao_protocolo",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nome", sa.String(200), nullable=False, unique=True),
        sa.Column("objetivo", sa.Text),
        sa.Column("restricoes", sa.JSON),
    )

    # ── L3 — usuario ──────────────────────────────────────────────────────────
    op.create_table(
        "usuario",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("sexo_biologico", sa.String(10)),
        sa.Column("data_nascimento", sa.Date),
        sa.Column("altura_cm", sa.Integer),
        sa.Column("objetivo_principal", sa.String(30)),
        sa.Column("nivel_atividade", sa.String(20)),
        sa.Column("restricoes", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "objetivo_principal IN ('emagrecimento','hipertrofia','performance','saude','reabilitacao') OR objetivo_principal IS NULL",
            name="ck_usuario_objetivo"
        ),
    )

    # ── L3 — perfil_fisiologico_snapshot ──────────────────────────────────────
    op.create_table(
        "perfil_fisiologico_snapshot",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scan_id", sa.String(36)),
        sa.Column("data_medicao", sa.DateTime(timezone=True), nullable=False),
        sa.Column("peso_kg", sa.Float),
        sa.Column("imc", sa.Float),
        sa.Column("circ_cintura", sa.Float),
        sa.Column("circ_quadril", sa.Float),
        sa.Column("circ_ombro", sa.Float),
        sa.Column("rcq", sa.Float),
        sa.Column("rca", sa.Float),
        sa.Column("perc_gordura", sa.Float),
        sa.Column("risco_cardiovascular", sa.String(20)),
        sa.Column("fonte", sa.String(20), nullable=False, server_default="manual"),
        sa.CheckConstraint("fonte IN ('bodyscan','manual','dispositivo')", name="ck_pfs_fonte"),
    )
    # Índice para série temporal (PRD seção 10)
    op.create_index("idx_pfs_usuario_data", "perfil_fisiologico_snapshot", ["usuario_id", "data_medicao"])

    # ── L4 — memoria_episodica ────────────────────────────────────────────────
    op.create_table(
        "memoria_episodica",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tipo_evento", sa.String(40), nullable=False),
        sa.Column("dominio", sa.String(20), nullable=False),
        sa.Column("ref_entidade_tipo", sa.String(50)),
        sa.Column("ref_entidade_id", sa.String(36)),
        sa.Column("payload", sa.JSON),
        sa.Column("ocorrido_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "tipo_evento IN ('scan_corporal','treino_realizado','refeicao_registrada','interacao_assistente','meta_definida','medicao')",
            name="ck_me_tipo_evento"
        ),
        sa.CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao','transversal')", name="ck_me_dominio"
        ),
    )

    # ── L4 — memoria_semantica ────────────────────────────────────────────────
    op.create_table(
        "memoria_semantica",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dominio", sa.String(20), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("afirmacao", sa.Text, nullable=False),
        sa.Column("confianca", sa.Float),
        sa.Column("evidencia_episodios", sa.JSON),
        sa.Column("valido_de", sa.DateTime(timezone=True)),
        sa.Column("valido_ate", sa.DateTime(timezone=True)),
        sa.Column("ativo", sa.Boolean, server_default="1"),
        sa.Column("embedding", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "dominio IN ('fisiologia','treino','nutricao','transversal')", name="ck_ms_dominio"
        ),
        sa.CheckConstraint(
            "tipo IN ('preferencia','restricao','padrao_comportamental','meta','insight_derivado')",
            name="ck_ms_tipo"
        ),
    )

    # ── L4 — memoria_vinculo_cross_dominio ────────────────────────────────────
    op.create_table(
        "memoria_vinculo_cross_dominio",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conceito_fisiologia_id", sa.String(36), sa.ForeignKey("concept.id")),
        sa.Column("conceito_treino_id", sa.String(36), sa.ForeignKey("concept.id")),
        sa.Column("conceito_nutricao_id", sa.String(36), sa.ForeignKey("concept.id")),
        sa.Column("tipo_vinculo", sa.String(30), nullable=False),
        sa.Column("descricao", sa.Text),
        sa.Column("forca", sa.Float),
        sa.Column("gerado_por", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("evidencia", sa.JSON),
        sa.Column("status", sa.String(20), nullable=False, server_default="hipotese"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint(
            "tipo_vinculo IN ('causa_efeito','sinergia','conflito','dependencia','compensacao')",
            name="ck_mvcd_tipo"
        ),
        sa.CheckConstraint(
            "status IN ('hipotese','validado','refutado')", name="ck_mvcd_status"
        ),
        sa.CheckConstraint(
            "(CASE WHEN conceito_fisiologia_id IS NOT NULL THEN 1 ELSE 0 END + "
            " CASE WHEN conceito_treino_id IS NOT NULL THEN 1 ELSE 0 END + "
            " CASE WHEN conceito_nutricao_id IS NOT NULL THEN 1 ELSE 0 END) >= 2",
            name="ck_mvcd_min_2_dominios"
        ),
    )

    # ── L4 — contexto_sessao ──────────────────────────────────────────────────
    op.create_table(
        "contexto_sessao",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sessao_id", sa.String(36), nullable=False),
        sa.Column("janela_contexto", sa.JSON),
        sa.Column("objetivo_sessao", sa.Text),
        sa.Column("expira_em", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── L5 — recuperacao_log ──────────────────────────────────────────────────
    op.create_table(
        "recuperacao_log",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("usuario_id", sa.String(36), sa.ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("dominios_consultados", sa.JSON),
        sa.Column("chunks_recuperados", sa.JSON),
        sa.Column("memorias_aplicadas", sa.JSON),
        sa.Column("resposta_gerada", sa.Text),
        sa.Column("feedback", sa.String(20)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    """Reverte todas as tabelas criadas no upgrade."""
    op.drop_table("recuperacao_log")
    op.drop_table("contexto_sessao")
    op.drop_table("memoria_vinculo_cross_dominio")
    op.drop_table("memoria_semantica")
    op.drop_table("memoria_episodica")
    op.drop_index("idx_pfs_usuario_data", table_name="perfil_fisiologico_snapshot")
    op.drop_table("perfil_fisiologico_snapshot")
    op.drop_table("usuario")
    op.drop_table("nutricao_protocolo")
    op.drop_table("nutricao_alimento")
    op.drop_table("treino_protocolo")
    op.drop_table("treino_exercicio")
    op.drop_table("fisiologia_marcador")
    op.drop_index("idx_cr_cross_domain", table_name="concept_relation")
    op.drop_table("concept_relation")
    op.drop_index("idx_chunk_dominio", table_name="knowledge_chunk")
    op.drop_table("knowledge_chunk")
    op.drop_table("concept")
    op.drop_table("knowledge_source")
