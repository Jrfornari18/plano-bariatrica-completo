"""
Serviço de recomendação: orquestra o pipeline RAG híbrido (RF-04/05/10, RNF-03/04).
Pseudocódigo do Anexo C do PRD implementado aqui.
"""
import json
import time
from typing import List, Optional, Dict, Any

from app.core.logging import get_logger
from app.models.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    TrainingPlan,
    TrainingBlock,
    TrainingItem,
)
from app.repositories import exercise_repo, profile_repo, recommendation_repo
from app.services import embedding_service
from app.services.llm import get_llm_provider, LLMError

logger = get_logger(__name__)

# ─── Schema 8.2 do PRD (para o prompt) ───────────────────────────────────────
SCHEMA_8_2 = """{
  "recomendacao_id": 0,
  "degraded": false,
  "treino": {
    "nome": "string",
    "modalidade": "string",
    "objetivo": "string",
    "nivel": "string",
    "duracao_min": 30,
    "estrutura": "string",
    "blocos": [
      {
        "bloco": "aquecimento|principal|finalizacao",
        "itens": [
          {
            "exercicio_id": 0,
            "nome": "string",
            "series": 1,
            "repeticoes": "string",
            "descanso_seg": 30,
            "alternativa": "string ou null",
            "regressao": "string ou null"
          }
        ]
      }
    ]
  },
  "justificativa": "string",
  "contexto_recuperado": [0]
}"""

SYSTEM_PROMPT_TEMPLATE = """Você é um prescritor de treinos. Monte UM treino usando EXCLUSIVAMENTE os exercícios
fornecidos no CONTEXTO. Nunca crie exercícios que não estejam no CONTEXTO.
Respeite o perfil (nível, objetivo, duração, local, restrições) e as contraindicações.
Use os TREINOS-EXEMPLO apenas como referência de formato.
Responda SOMENTE com JSON válido no schema fornecido, sem texto fora do JSON.
Inclua o campo "justificativa" explicando as escolhas em 2–3 frases.

PERFIL: {perfil}
RESTRIÇÕES: {restricoes}
CONTEXTO (exercícios recuperados): {documentos_top_k}
TREINOS-EXEMPLO: {few_shot}
SCHEMA DE SAÍDA: {schema}"""


async def recomendar(req: RecommendationRequest) -> RecommendationResponse:
    """
    Orquestra o pipeline RAG híbrido completo:
    RF-02 → RF-03 → RF-04 → RF-10 → RF-06
    """
    t0 = time.monotonic()

    # ── Resolver perfil ──────────────────────────────────────────────────────
    perfil_data: Dict[str, Any] = {}
    if req.perfil_id:
        perfil_data = await profile_repo.get_profile(req.perfil_id) or {}

    nivel = req.nivel or perfil_data.get("nivel_experiencia") or "iniciante"
    local = req.local or perfil_data.get("local_preferido") or "casa"
    restricoes = req.restricoes or (
        [r.strip() for r in perfil_data.get("restricoes", "").split(",")]
        if perfil_data.get("restricoes")
        else []
    )
    equipamentos = req.equipamentos_disponiveis or (
        [e.strip() for e in perfil_data.get("equipamentos_disponiveis", "").split(",")]
        if perfil_data.get("equipamentos_disponiveis")
        else None
    )

    # ── F2: Filtro estruturado (RF-02) ───────────────────────────────────────
    t_filter = time.monotonic()
    candidatos = await exercise_repo.filtrar_candidatos(
        modalidades=req.modalidades,
        nivel=nivel,
        equipamentos_disponiveis=equipamentos,
        excluir_contraindicacoes=restricoes if restricoes else None,
        local=local,
    )
    logger.info(
        "F2 filtro: %d candidatos em %.0fms",
        len(candidatos),
        (time.monotonic() - t_filter) * 1000,
        extra={"rag_step": "filter", "candidates_count": len(candidatos), "duration_ms": int((time.monotonic() - t_filter) * 1000)},
    )

    if not candidatos:
        # Fallback: sem filtro de modalidade
        candidatos = await exercise_repo.filtrar_candidatos(
            nivel=nivel,
            excluir_contraindicacoes=restricoes if restricoes else None,
        )

    candidate_ids = [c["id"] for c in candidatos]
    candidatos_map = {c["id"]: c for c in candidatos}

    # ── F3: Recuperação semântica (RF-03) ────────────────────────────────────
    t_retrieval = time.monotonic()
    top_k_results = embedding_service.search_similar(
        query=req.intencao,
        candidate_ids=candidate_ids,
        top_k=req.top_k,
    )
    logger.info(
        "F3 retrieval: top-%d em %.0fms",
        len(top_k_results),
        (time.monotonic() - t_retrieval) * 1000,
        extra={"rag_step": "retrieval", "top_k_count": len(top_k_results), "duration_ms": int((time.monotonic() - t_retrieval) * 1000)},
    )

    # Se não há resultados semânticos, usar os primeiros candidatos
    if not top_k_results:
        top_k_results = [{"exercicio_id": eid, "score": 1.0} for eid in candidate_ids[:req.top_k]]

    top_k_ids = [r["exercicio_id"] for r in top_k_results]
    top_k_docs = [candidatos_map[eid]["documento"] for eid in top_k_ids if eid in candidatos_map]

    # ── Montar contexto ──────────────────────────────────────────────────────
    few_shot = await exercise_repo.get_few_shot_treinos()
    few_shot_text = json.dumps(few_shot[:3], ensure_ascii=False, indent=2)

    perfil_summary = {
        "nivel": nivel,
        "objetivo": req.intencao,
        "duracao_min": req.duracao_min or 30,
        "local": local,
        "restricoes": restricoes,
        "equipamentos": equipamentos or ["Peso corporal"],
        "imc": perfil_data.get("imc"),
        "rcq": perfil_data.get("rcq"),
        "rca": perfil_data.get("rca"),
    }

    prompt_system = SYSTEM_PROMPT_TEMPLATE.format(
        perfil=json.dumps(perfil_summary, ensure_ascii=False),
        restricoes=", ".join(restricoes) if restricoes else "nenhuma",
        documentos_top_k="\n\n".join(top_k_docs),
        few_shot=few_shot_text,
        schema=SCHEMA_8_2,
    )
    prompt_user = f"Intenção do usuário: {req.intencao}"

    # ── F4/F5: Geração LLM + fallback (RF-04, RNF-03) ───────────────────────
    degraded = False
    treino_dict: Dict[str, Any] = {}

    llm = get_llm_provider()
    if llm.is_available():
        try:
            t_llm = time.monotonic()
            raw_response = await llm.generate(prompt_system, prompt_user)
            logger.info(
                "F4 LLM: gerado em %.0fms",
                (time.monotonic() - t_llm) * 1000,
                extra={"rag_step": "generation", "duration_ms": int((time.monotonic() - t_llm) * 1000)},
            )
            treino_dict = json.loads(raw_response)

            # ── Validação anti-alucinação (RNF-04) ──────────────────────────
            treino_dict = _validar_anti_alucinacao(treino_dict, set(top_k_ids))

        except (LLMError, json.JSONDecodeError, ValueError) as exc:
            logger.warning("LLM falhou (%s) — usando fallback por regras", exc)
            degraded = True
    else:
        logger.info("LLM não configurado — usando fallback por regras")
        degraded = True

    if degraded or not treino_dict:
        treino_dict = _montar_por_regras(
            top_k_results=top_k_results,
            candidatos_map=candidatos_map,
            perfil=perfil_summary,
        )
        degraded = True

    # ── RF-10: Enriquecer alternativas e progressões ─────────────────────────
    treino_dict = await _enriquecer_alternativas_progressoes(treino_dict)

    # ── RF-06: Persistência ──────────────────────────────────────────────────
    rec_id = await recommendation_repo.save_recommendation(
        perfil_id=req.perfil_id,
        prompt=prompt_system[:2000],  # truncar para não exceder coluna
        contexto_rag=top_k_ids,
        resposta=treino_dict,
    )

    total_ms = int((time.monotonic() - t0) * 1000)
    logger.info("Pipeline RAG completo em %dms, rec_id=%d, degraded=%s", total_ms, rec_id, degraded)

    # ── Montar resposta ──────────────────────────────────────────────────────
    treino_obj = _dict_to_training_plan(treino_dict, perfil_summary)

    return RecommendationResponse(
        recomendacao_id=rec_id,
        degraded=degraded,
        treino=treino_obj,
        justificativa=treino_dict.get("justificativa", "Treino gerado com base no seu perfil e intenção."),
        contexto_recuperado=top_k_ids,
    )


def _validar_anti_alucinacao(treino_dict: Dict[str, Any], allowed_ids: set) -> Dict[str, Any]:
    """
    RNF-04: Remove exercícios que não estão no contexto recuperado.
    Lança ValueError se o treino ficar vazio após a limpeza.
    """
    blocos = treino_dict.get("treino", {}).get("blocos", [])
    cleaned_blocos = []
    removed = 0

    for bloco in blocos:
        itens_validos = []
        for item in bloco.get("itens", []):
            eid = item.get("exercicio_id")
            if eid in allowed_ids:
                itens_validos.append(item)
            else:
                removed += 1
                logger.warning(
                    "Anti-alucinação: exercício_id=%s removido (não estava no contexto)", eid
                )
        if itens_validos:
            cleaned_blocos.append({**bloco, "itens": itens_validos})

    if removed > 0:
        logger.info("Anti-alucinação: %d exercício(s) removido(s)", removed)

    if not cleaned_blocos:
        raise ValueError("Todos os exercícios gerados pelo LLM estavam fora do contexto (alucinação total)")

    treino_dict["treino"]["blocos"] = cleaned_blocos
    return treino_dict


def _montar_por_regras(
    top_k_results: List[Dict],
    candidatos_map: Dict[int, Any],
    perfil: Dict[str, Any],
) -> Dict[str, Any]:
    """
    RNF-03: Fallback por regras quando o LLM falha.
    Monta um treino básico ordenando candidatos por score.
    """
    duracao = perfil.get("duracao_min", 30)
    nivel = perfil.get("nivel", "iniciante")

    blocos_map: Dict[str, List] = {"aquecimento": [], "principal": [], "finalizacao": []}
    for i, result in enumerate(top_k_results):
        eid = result["exercicio_id"]
        ex = candidatos_map.get(eid, {})
        item = {
            "exercicio_id": eid,
            "nome": ex.get("nome", f"Exercício {eid}"),
            "series": 3,
            "repeticoes": "12",
            "descanso_seg": 30,
            "alternativa": None,
            "regressao": None,
        }
        if i == 0:
            item["series"] = 1
            item["repeticoes"] = "60s"
            item["descanso_seg"] = 15
            blocos_map["aquecimento"].append(item)
        elif i >= len(top_k_results) - 1:
            item["series"] = 1
            item["repeticoes"] = "60s"
            item["descanso_seg"] = 0
            blocos_map["finalizacao"].append(item)
        else:
            blocos_map["principal"].append(item)

    blocos = [
        {"bloco": bloco, "itens": itens}
        for bloco, itens in blocos_map.items()
        if itens
    ]

    return {
        "treino": {
            "nome": "Treino Personalizado (modo básico)",
            "modalidade": "funcional",
            "objetivo": perfil.get("objetivo", "condicionamento"),
            "nivel": nivel,
            "duracao_min": duracao,
            "estrutura": "sequencial",
            "blocos": blocos,
        },
        "justificativa": "Treino montado por regras (modo degradado). Os exercícios foram selecionados com base no seu perfil e disponibilidade de equipamentos.",
        "contexto_recuperado": [r["exercicio_id"] for r in top_k_results],
    }


async def _enriquecer_alternativas_progressoes(treino_dict: Dict[str, Any]) -> Dict[str, Any]:
    """RF-10: Adiciona alternativas e progressões/regressões do banco (não inventadas pelo LLM)."""
    blocos = treino_dict.get("treino", {}).get("blocos", [])
    for bloco in blocos:
        for item in bloco.get("itens", []):
            eid = item.get("exercicio_id")
            if not eid:
                continue
            try:
                enrich = await exercise_repo.get_alternativas_progressoes(eid)
                # Só sobrescreve se o LLM não preencheu
                if not item.get("alternativa") and enrich["alternativas"]:
                    item["alternativa"] = enrich["alternativas"][0]["nome"]
                if not item.get("regressao") and enrich["regressao"]:
                    item["regressao"] = enrich["regressao"]["nome"]
                if not item.get("progressao") and enrich["progressao"]:
                    item["progressao"] = enrich["progressao"]["nome"]
            except Exception as exc:
                logger.warning("Falha ao enriquecer exercício %s: %s", eid, exc)
    return treino_dict


def _dict_to_training_plan(treino_dict: Dict[str, Any], perfil: Dict[str, Any]) -> TrainingPlan:
    """Converte o dicionário do treino para o modelo Pydantic TrainingPlan."""
    treino_raw = treino_dict.get("treino", {})
    blocos = []
    for bloco_raw in treino_raw.get("blocos", []):
        itens = []
        for item_raw in bloco_raw.get("itens", []):
            itens.append(TrainingItem(
                exercicio_id=item_raw.get("exercicio_id", 0),
                nome=item_raw.get("nome", ""),
                series=item_raw.get("series", 3),
                repeticoes=str(item_raw.get("repeticoes", "12")),
                descanso_seg=item_raw.get("descanso_seg", 30),
                alternativa=item_raw.get("alternativa"),
                regressao=item_raw.get("regressao"),
                progressao=item_raw.get("progressao"),
            ))
        blocos.append(TrainingBlock(bloco=bloco_raw.get("bloco", "principal"), itens=itens))

    return TrainingPlan(
        nome=treino_raw.get("nome", "Treino Personalizado"),
        modalidade=treino_raw.get("modalidade", "funcional"),
        objetivo=treino_raw.get("objetivo", perfil.get("objetivo", "condicionamento")),
        nivel=treino_raw.get("nivel", perfil.get("nivel", "iniciante")),
        duracao_min=treino_raw.get("duracao_min", perfil.get("duracao_min", 30)),
        estrutura=treino_raw.get("estrutura", "sequencial"),
        blocos=blocos,
    )
