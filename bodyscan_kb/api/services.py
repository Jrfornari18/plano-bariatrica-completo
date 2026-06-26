"""
services.py — Serviços de suporte para a API BodyScan KB.

Inclui:
  - gerar_recomendacao_llm: geração com grounding e citação (RF-06)
  - registrar_log: auditoria de cada recomendação (RF-09)
  - registrar_feedback: coleta de feedback (RF-10)
"""

from __future__ import annotations

import json
import os
from typing import Any

import asyncpg
import openai

# -------------------------------------------------------------------------
# Geração LLM com grounding e citação (RF-06)
# -------------------------------------------------------------------------

SYSTEM_PROMPT = """Você é um assistente educativo de fisiologia do emagrecimento para o BodyScan.

REGRAS OBRIGATÓRIAS (não podem ser violadas):
1. Responda APENAS com base nos chunks de conhecimento fornecidos.
2. Cite as fontes pelo campo 'dominio_slug' ou 'nivel_evidencia' dos chunks.
3. NÃO prescreva fármacos, doses específicas ou metas calóricas individuais.
4. NÃO emita planos nutricionais numéricos individuais sem profissional.
5. Se o tema exigir supervisão médica, oriente explicitamente a buscar profissional.
6. Se não houver chunks relevantes, recuse e informe que o tema não está coberto.
7. Seja educativo, claro e seguro. Não invente informações.
8. Sempre inclua disclaimer: "Esta informação é educativa e não substitui orientação profissional."

PROIBIÇÕES ABSOLUTAS:
- Prescrever ou validar uso off-label de medicamentos
- Emitir metas de perda de peso numéricas individuais
- Aconselhar restrição calórica extrema
- Validar sintomas clínicos sem encaminhar a profissional
"""


async def gerar_recomendacao_llm(
    pergunta: str,
    chunks: list[dict[str, Any]],
    recomendacoes: list[dict[str, Any]] | None = None,
    contexto_clinico: str | None = None,
) -> str:
    """Gera resposta ancorada nos chunks via LLM.

    Implementa RF-06: resposta baseada apenas nos chunks recuperados, com citação.
    Implementa RF-12: recusa quando não há chunks relevantes.
    """
    if not chunks:
        return (
            "Não encontrei informações na base de conhecimento que cubram este tema. "
            "Por favor, consulte um profissional de saúde habilitado para orientações específicas. "
            "Esta informação é educativa e não substitui orientação profissional."
        )

    # Monta contexto com chunks
    contexto_chunks = "\n\n".join([
        f"[Chunk {i+1} | Domínio: {c.get('dominio_slug','?')} | "
        f"Evidência: {c.get('nivel_evidencia','?')}]\n{c['texto']}"
        for i, c in enumerate(chunks)
    ])

    # Monta contexto com recomendações elegíveis
    contexto_recs = ""
    if recomendacoes:
        recs_txt = "\n".join([
            f"- {r['titulo']} (força: {r['forca']})"
            for r in recomendacoes
        ])
        contexto_recs = f"\n\nRECOMENDAÇÕES ELEGÍVEIS PARA O CONTEXTO:\n{recs_txt}"

    contexto_clinico_txt = (
        f"\nCONTEXTO CLÍNICO DO USUÁRIO: {contexto_clinico}" if contexto_clinico else ""
    )

    user_message = f"""PERGUNTA DO USUÁRIO: {pergunta}
{contexto_clinico_txt}

CHUNKS DE CONHECIMENTO DISPONÍVEIS:
{contexto_chunks}
{contexto_recs}

Responda à pergunta baseando-se EXCLUSIVAMENTE nos chunks acima.
Cite as fontes mencionando o domínio e nível de evidência.
Inclua o disclaimer obrigatório ao final."""

    try:
        client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
        )
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,  # Baixa temperatura para respostas mais factuais
            max_tokens=1000,
        )
        return response.choices[0].message.content or "Resposta não disponível."

    except Exception as e:
        # Fallback: retorna os chunks diretamente sem LLM
        fallback = (
            f"[Modo fallback — LLM indisponível: {type(e).__name__}]\n\n"
            "Com base na base de conhecimento:\n\n"
        )
        for i, c in enumerate(chunks[:3], 1):
            fallback += f"{i}. {c['texto'][:300]}...\n\n"
        fallback += (
            "\nFonte: Base de conhecimento BodyScan KB. "
            "Esta informação é educativa e não substitui orientação profissional."
        )
        return fallback


# -------------------------------------------------------------------------
# Auditoria: registra log de recomendação (RF-09)
# -------------------------------------------------------------------------
async def registrar_log(
    pool: asyncpg.Pool,
    perfil_pseudonimo: str | None,
    recomendacao_id: str | None,
    chunks_ids: list[str],
    modelo: str,
    prompt_hash: str,
    houve_escalonamento: bool,
    tipo_alerta: str | None,
) -> str | None:
    """Registra log de auditoria para cada recomendação emitida.

    RF-09: cada resposta gera log com chunks usados, modelo e flag de escalonamento.
    """
    try:
        async with pool.acquire() as con:
            # Busca ou cria perfil pelo pseudônimo
            perfil_id = None
            if perfil_pseudonimo:
                row = await con.fetchrow(
                    "SELECT id FROM perfil_usuario WHERE pseudonimo = $1",
                    perfil_pseudonimo,
                )
                if row:
                    perfil_id = row["id"]

            # Converte chunks_ids para array de UUIDs
            chunks_uuids = None
            if chunks_ids:
                try:
                    from uuid import UUID
                    chunks_uuids = [UUID(cid) for cid in chunks_ids]
                except Exception:
                    chunks_uuids = None

            log_id = await con.fetchval(
                """
                INSERT INTO log_recomendacao
                    (perfil_id, recomendacao_id, chunks_recuperados,
                     modelo_gerador, prompt_hash,
                     houve_escalonamento, tipo_alerta_disparado)
                VALUES ($1, $2, $3, $4, $5, $6, $7::tipo_alerta)
                RETURNING id
                """,
                perfil_id,
                None,  # recomendacao_id — pode ser NULL para respostas RAG
                chunks_uuids,
                modelo,
                prompt_hash,
                houve_escalonamento,
                tipo_alerta,
            )
            return str(log_id)
    except Exception as e:
        print(f"[WARN] Falha ao registrar log: {e}")
        return None


# -------------------------------------------------------------------------
# Feedback: registra avaliação do usuário (RF-10)
# -------------------------------------------------------------------------
async def registrar_feedback(
    pool: asyncpg.Pool,
    log_id: str,
    util: bool | None,
    comentario: str | None,
) -> None:
    """Registra feedback vinculado ao log de recomendação.

    RF-10: feedback persistido e vinculado ao log.
    """
    async with pool.acquire() as con:
        # Verifica se o log existe
        log_row = await con.fetchrow(
            "SELECT id FROM log_recomendacao WHERE id = $1::uuid",
            log_id,
        )
        if not log_row:
            raise ValueError(f"Log não encontrado: {log_id}")

        await con.execute(
            """
            INSERT INTO feedback_recomendacao (log_id, util, comentario)
            VALUES ($1::uuid, $2, $3)
            """,
            log_id,
            util,
            comentario,
        )
