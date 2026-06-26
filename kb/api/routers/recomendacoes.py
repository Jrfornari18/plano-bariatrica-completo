"""
recomendacoes.py — Router de recomendações com gates de governança clínica.

POST /v1/recomendacoes
  Fluxo: gate_escalonamento → recuperar → regras → LLM(grounding) → log

Governança (seção 8 do PRD):
  1. Gate de escalonamento: bloqueia sinais de risco
  2. Gate de conteúdo servível: exclui conteúdo sem evidência ou que exige supervisão
  3. Sem números individuais: proibido emitir dose/meta calórica
  4. Grounding + citação obrigatórios
  5. Auditoria: toda saída registrada em log_recomendacao
  6. RF-12: recusa quando KB não cobre o tema
"""
from __future__ import annotations

import logging
from typing import Union

from fastapi import APIRouter, Depends, HTTPException

from ..database import get_pool
from ..models.schemas import (
    RecomendacaoRequest,
    RecomendacaoResponse,
    EscalonamentoResponse,
    NaoCobertoResponse,
    ChunkResponse,
    RecomendacaoItem,
)
from ..services.recuperacao import (
    avaliar_gatilhos,
    recuperar,
    recomendacoes_elegiveis_por_metrica,
)
from ..services.geracao import gerar_resposta
from ..services.auditoria import (
    obter_ou_criar_perfil,
    registrar_metricas,
    registrar_log,
    buscar_fontes_dos_chunks,
)
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/recomendacoes", tags=["recomendacoes"])


@router.post(
    "",
    response_model=Union[RecomendacaoResponse, EscalonamentoResponse, NaoCobertoResponse],
    summary="Gera recomendação educativa com governança clínica",
    description=(
        "Orquestra: gate de escalonamento → recuperação híbrida → "
        "camada de regras → geração LLM com grounding → auditoria. "
        "Retorna desvio se detectar sinais de risco."
    ),
)
async def post_recomendacao(
    req: RecomendacaoRequest,
    pool=Depends(get_pool),
):
    settings = get_settings()

    # ------------------------------------------------------------------
    # 1. Gate de escalonamento (human-in-the-loop)
    # RF-07: entradas com termos de risco retornam escalonar=true
    # ------------------------------------------------------------------
    gate = await avaliar_gatilhos(pool, req.pergunta)

    if gate.bloqueado:
        logger.warning(
            "Escalonamento: pseudonimo=%s tipo=%s acao=%s",
            req.pseudonimo,
            gate.tipo_alerta,
            gate.acao,
        )
        # Registra log de escalonamento
        perfil_id = await obter_ou_criar_perfil(pool, req.pseudonimo, req.contexto_clinico)
        await registrar_log(
            pool=pool,
            perfil_id=perfil_id,
            recomendacao_id=None,
            chunks=[],
            modelo="gate_escalonamento",
            prompt_hash="",
            houve_escalonamento=True,
            tipo_alerta=gate.tipo_alerta,
        )
        return EscalonamentoResponse(
            tipo_alerta=gate.tipo_alerta,
            acao=gate.acao,
        )

    # ------------------------------------------------------------------
    # 2. Recuperação híbrida com gate de conteúdo servível
    # RF-04: recuperar() filtrado por contexto + gate de supervisão
    # RF-08: chunks de supervisão excluídos quando incluir_supervisao=False
    # ------------------------------------------------------------------
    contextos = [req.contexto_clinico] if req.contexto_clinico else None
    chunks = await recuperar(
        pool=pool,
        consulta=req.pergunta,
        contextos=contextos,
        incluir_supervisao=req.incluir_supervisao,
        k=req.k,
    )

    # ------------------------------------------------------------------
    # 3. Perfil e métricas (RF-11, RNF-03)
    # ------------------------------------------------------------------
    perfil_id = await obter_ou_criar_perfil(pool, req.pseudonimo, req.contexto_clinico)
    metricas_dict = {m.biomarcador: m.valor for m in req.metricas}

    if req.metricas:
        await registrar_metricas(
            pool=pool,
            perfil_id=perfil_id,
            metricas=[m.model_dump() for m in req.metricas],
        )

    # ------------------------------------------------------------------
    # 4. Camada de regras: recomendações elegíveis por contexto + métrica
    # RF-05: condição de métrica avaliada
    # ------------------------------------------------------------------
    recs_elegiveis = []
    if req.contexto_clinico:
        recs_elegiveis = await recomendacoes_elegiveis_por_metrica(
            pool=pool,
            contexto_slug=req.contexto_clinico,
            metricas=metricas_dict,
            incluir_supervisao=req.incluir_supervisao,
        )

    # ------------------------------------------------------------------
    # 5. Busca fontes dos chunks para citação
    # ------------------------------------------------------------------
    chunk_ids = [c.id for c in chunks]
    fontes = await buscar_fontes_dos_chunks(pool, chunk_ids)

    # ------------------------------------------------------------------
    # 6. Geração LLM com grounding obrigatório
    # RF-06: resposta ancorada nos chunks recuperados com fontes citadas
    # RF-12: sem chunks → recusa explícita
    # ------------------------------------------------------------------
    resposta_texto, prompt_hash = await gerar_resposta(
        pergunta=req.pergunta,
        chunks=chunks,
        fontes=fontes,
    )

    # ------------------------------------------------------------------
    # 7. Registro de auditoria (RF-09, RNF-04)
    # ------------------------------------------------------------------
    rec_id = recs_elegiveis[0].id if recs_elegiveis else None
    log_id = await registrar_log(
        pool=pool,
        perfil_id=perfil_id,
        recomendacao_id=rec_id,
        chunks=chunks,
        modelo=settings.openai_chat_model,
        prompt_hash=prompt_hash,
        houve_escalonamento=False,
        tipo_alerta=None,
    )

    # ------------------------------------------------------------------
    # 8. RF-12: sem chunks → resposta de não-cobertura
    # ------------------------------------------------------------------
    if not chunks:
        return NaoCobertoResponse(log_id=log_id)

    return RecomendacaoResponse(
        resposta=resposta_texto,
        recomendacoes=[
            RecomendacaoItem(
                slug=r.slug,
                titulo=r.titulo,
                forca=r.forca,
                requer_supervisao=r.requer_supervisao,
            )
            for r in recs_elegiveis
        ],
        chunks=[
            ChunkResponse(
                id=c.id,
                texto=c.texto,
                distancia=c.distancia,
                requer_supervisao=c.requer_supervisao,
                dominio_slug=c.dominio_slug,
                contexto_slugs=c.contexto_slugs,
                nivel_evidencia=c.nivel_evidencia,
            )
            for c in chunks
        ],
        fontes=fontes,
        log_id=log_id,
    )
