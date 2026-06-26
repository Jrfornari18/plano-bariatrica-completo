"""
geracao.py — Serviço de geração de resposta via LLM com grounding obrigatório.

Governança (seção 8 do PRD):
  - Resposta APENAS com base nos chunks recuperados (grounding)
  - Citação de fontes obrigatória
  - Proibido: dose de fármaco, meta calórica numérica, plano individual
  - Sem chunk → recusa (RF-12)
  - Prompt hash registrado para auditoria
"""
from __future__ import annotations

import hashlib
import logging
import os
from typing import Sequence

from ..config import get_settings
from ..services.recuperacao import ChunkRecuperado

logger = logging.getLogger(__name__)

# System prompt de governança clínica — NÃO MODIFICAR sem revisão profissional
SYSTEM_PROMPT = """Você é um assistente educativo de saúde do sistema BodyScan, especializado em fisiologia do emagrecimento pós-bariátrico e uso de fármacos antiobesidade.

REGRAS ABSOLUTAS (não negociáveis):
1. Responda APENAS com base nos trechos de conhecimento fornecidos abaixo. Não use conhecimento externo para claims clínicos.
2. Cite as fontes dos trechos usados na resposta (ex.: "[Fonte: ASMBS Guidelines]").
3. NUNCA prescreva fármacos, doses ou metas calóricas numéricas individuais.
4. NUNCA valide uso off-label de medicamentos.
5. NUNCA emita plano nutricional individual sem supervisão profissional.
6. Se os trechos não cobrirem a pergunta, diga claramente que não tem informação suficiente.
7. Sempre inclua o aviso: "Esta informação é educativa e não substitui avaliação médica ou nutricional."

FORMATO DA RESPOSTA:
- Resposta clara e educativa em português
- Cite fontes entre colchetes ao final de cada afirmação relevante
- Termine com o aviso obrigatório
"""

INSTRUCAO_GROUNDING = """
TRECHOS DE CONHECIMENTO DISPONÍVEIS:
{chunks_texto}

PERGUNTA DO USUÁRIO: {pergunta}

Responda baseando-se EXCLUSIVAMENTE nos trechos acima. Cite as fontes.
"""


def _hash_prompt(prompt: str) -> str:
    """Gera hash SHA-256 do prompt para auditoria."""
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def _formatar_chunks(chunks: Sequence[ChunkRecuperado]) -> str:
    """Formata chunks para o prompt de grounding."""
    if not chunks:
        return "(nenhum trecho disponível)"
    partes = []
    for i, c in enumerate(chunks, start=1):
        partes.append(f"[Trecho {i}] {c.texto}")
    return "\n\n".join(partes)


async def gerar_resposta(
    pergunta: str,
    chunks: Sequence[ChunkRecuperado],
    fontes: list[str] | None = None,
) -> tuple[str, str]:
    """
    Gera resposta via LLM com grounding nos chunks fornecidos.

    Retorna (resposta_texto, prompt_hash).

    Se não houver chunks, retorna mensagem de não-cobertura (RF-12).
    """
    if not chunks:
        resposta = (
            "Não encontrei informações suficientes na base de conhecimento para "
            "responder a esta pergunta com segurança. Por favor, consulte um "
            "profissional de saúde habilitado."
        )
        return resposta, _hash_prompt(pergunta)

    settings = get_settings()
    chunks_texto = _formatar_chunks(chunks)
    prompt_usuario = INSTRUCAO_GROUNDING.format(
        chunks_texto=chunks_texto,
        pergunta=pergunta,
    )
    prompt_hash = _hash_prompt(SYSTEM_PROMPT + prompt_usuario)

    try:
        from openai import AsyncOpenAI
        base_url = os.environ.get("OPENAI_API_BASE", settings.openai_api_base)
        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=base_url,
        )

        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_usuario},
            ],
            temperature=0.2,  # Baixa temperatura para respostas mais factuais
            max_tokens=1024,
        )
        resposta = response.choices[0].message.content or ""
        logger.info(
            "LLM gerou resposta: model=%s hash=%s chunks=%d",
            settings.openai_chat_model,
            prompt_hash,
            len(chunks),
        )

    except Exception as exc:
        logger.error("Erro na geração LLM: %s — usando fallback educativo", exc)
        # Fallback: resposta estruturada baseada nos chunks sem LLM
        resposta = _gerar_resposta_fallback(pergunta, chunks, fontes or [])

    return resposta, prompt_hash


def _gerar_resposta_fallback(
    pergunta: str,
    chunks: Sequence[ChunkRecuperado],
    fontes: list[str],
) -> str:
    """
    Fallback educativo quando a LLM não está disponível.
    Apresenta os chunks de forma estruturada com aviso.
    """
    partes = [
        f"Com base nas informações disponíveis sobre '{pergunta}':\n"
    ]
    for i, c in enumerate(chunks, start=1):
        partes.append(f"{i}. {c.texto}")

    if fontes:
        partes.append(f"\nFontes: {', '.join(fontes)}")

    partes.append(
        "\n⚠️ Esta informação é educativa e não substitui avaliação médica ou nutricional. "
        "Consulte um profissional de saúde habilitado."
    )
    return "\n\n".join(partes)
