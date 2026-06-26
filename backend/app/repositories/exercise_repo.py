"""
Repositório de exercícios: filtro estruturado SQL (RF-02) e catálogo (RF-08).
"""
from typing import List, Optional, Dict, Any
import aiosqlite
from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)


async def filtrar_candidatos(
    modalidades: Optional[List[str]] = None,
    nivel: Optional[str] = None,
    equipamentos_disponiveis: Optional[List[str]] = None,
    excluir_contraindicacoes: Optional[List[str]] = None,
    local: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    RF-02: Filtro estruturado SQL que reduz o universo de candidatos.
    - Filtra por modalidade, nível e equipamentos disponíveis.
    - Exclui exercícios com contraindicações que coincidam com as restrições do usuário.
    - Exclui exercícios que requerem academia se local='casa'.
    """
    params: List[Any] = []
    conditions: List[str] = []

    base_query = """
        SELECT
            e.id,
            e.nome,
            e.slug,
            e.nivel_dificuldade,
            e.descricao,
            e.instrucoes_execucao,
            e.dicas_tecnica,
            e.contraindicacoes,
            e.met,
            e.composto,
            e.exercicio_regressao_id,
            e.exercicio_progressao_id,
            m.nome AS modalidade,
            m.slug AS modalidade_slug,
            v.documento
        FROM exercicios e
        JOIN modalidades m ON e.modalidade_id = m.id
        LEFT JOIN vw_exercicios_documento v ON v.exercicio_id = e.id
    """

    # Filtro por modalidade
    if modalidades:
        slugs = [_normalise_modalidade(mod) for mod in modalidades]
        placeholders = ",".join("?" for _ in slugs)
        conditions.append(f"m.slug IN ({placeholders})")
        params.extend(slugs)

    # Filtro por nível (iniciante pode fazer iniciante; intermediário pode fazer iniciante e intermediário)
    if nivel:
        nivel_order = {"iniciante": 1, "intermediario": 2, "avancado": 3}
        max_order = nivel_order.get(nivel, 3)
        conditions.append("""
            e.nivel_dificuldade IN (
                SELECT nd.nome FROM niveis_dificuldade nd WHERE nd.ordem <= ?
            )
        """)
        params.append(max_order)

    # Filtro por local: se 'casa', excluir equipamentos que requerem academia
    if local and local.lower() == "casa":
        conditions.append("""
            e.id NOT IN (
                SELECT ee.exercicio_id
                FROM exercicio_equipamentos ee
                JOIN equipamentos eq ON ee.equipamento_id = eq.id
                WHERE eq.requer_academia = 1
            )
        """)

    # Filtro por equipamentos disponíveis
    if equipamentos_disponiveis:
        # Inclui exercícios que usam APENAS equipamentos disponíveis (ou peso corporal)
        # Lógica: exercício é válido se todos os seus equipamentos estão na lista disponível
        # OU se o exercício não requer nenhum equipamento especial
        placeholders = ",".join("?" for _ in equipamentos_disponiveis)
        conditions.append(f"""
            e.id NOT IN (
                SELECT ee.exercicio_id
                FROM exercicio_equipamentos ee
                JOIN equipamentos eq ON ee.equipamento_id = eq.id
                WHERE eq.nome NOT IN ({placeholders})
                  AND eq.tipo != 'peso_corporal'
                  AND eq.tipo != 'nenhum'
            )
        """)
        params.extend(equipamentos_disponiveis)

    # Exclusão de contraindicações (RF-02 — segurança)
    if excluir_contraindicacoes:
        for restricao in excluir_contraindicacoes:
            conditions.append("(e.contraindicacoes IS NULL OR LOWER(e.contraindicacoes) NOT LIKE ?)")
            params.append(f"%{restricao.lower()}%")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    query = f"{base_query} {where_clause} ORDER BY e.id"

    async with get_db() as conn:
        async with conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()

    candidatos = [dict(row) for row in rows]
    logger.info(
        "Filtro estruturado retornou %d candidatos",
        len(candidatos),
        extra={"rag_step": "filter", "candidates_count": len(candidatos)},
    )
    return candidatos


async def get_exercise_by_id(exercise_id: int) -> Optional[Dict[str, Any]]:
    """RF-08: Detalhe de um exercício com músculos, equipamentos, objetivos e alternativas."""
    async with get_db() as conn:
        async with conn.execute(
            "SELECT e.*, m.nome AS modalidade FROM exercicios e JOIN modalidades m ON e.modalidade_id = m.id WHERE e.id = ?",
            (exercise_id,),
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            return None
        exercise = dict(row)

        # Músculos
        async with conn.execute(
            """SELECT gm.nome, em.papel FROM exercicio_musculos em JOIN grupos_musculares gm ON em.grupo_muscular_id = gm.id WHERE em.exercicio_id = ?""",
            (exercise_id,),
        ) as cursor:
            exercise["musculos"] = [f"{r['nome']} ({r['papel']})" for r in await cursor.fetchall()]

        # Equipamentos
        async with conn.execute(
            "SELECT eq.nome FROM exercicio_equipamentos ee JOIN equipamentos eq ON ee.equipamento_id = eq.id WHERE ee.exercicio_id = ?",
            (exercise_id,),
        ) as cursor:
            exercise["equipamentos"] = [r["nome"] for r in await cursor.fetchall()]

        # Objetivos
        async with conn.execute(
            "SELECT o.nome, eo.eficacia FROM exercicio_objetivos eo JOIN objetivos o ON eo.objetivo_id = o.id WHERE eo.exercicio_id = ?",
            (exercise_id,),
        ) as cursor:
            exercise["objetivos"] = [f"{r['nome']} (eficácia {r['eficacia']}/5)" for r in await cursor.fetchall()]

        # Alternativas
        async with conn.execute(
            "SELECT ea.alternativa_id FROM exercicio_alternativas ea WHERE ea.exercicio_id = ?",
            (exercise_id,),
        ) as cursor:
            exercise["alternativas"] = [r["alternativa_id"] for r in await cursor.fetchall()]

        # Regressão/progressão nomes
        if exercise.get("exercicio_regressao_id"):
            async with conn.execute("SELECT nome FROM exercicios WHERE id = ?", (exercise["exercicio_regressao_id"],)) as c:
                r = await c.fetchone()
                exercise["regressao_nome"] = r["nome"] if r else None
        if exercise.get("exercicio_progressao_id"):
            async with conn.execute("SELECT nome FROM exercicios WHERE id = ?", (exercise["exercicio_progressao_id"],)) as c:
                r = await c.fetchone()
                exercise["progressao_nome"] = r["nome"] if r else None

    return exercise


async def list_exercises(
    modalidade: Optional[str] = None,
    nivel: Optional[str] = None,
    objetivo: Optional[str] = None,
    equipamento: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """RF-08: Listagem de exercícios com filtros combináveis."""
    conditions: List[str] = []
    params: List[Any] = []

    base = """
        SELECT DISTINCT e.id, e.nome, e.slug, e.nivel_dificuldade, e.descricao,
               e.contraindicacoes, e.met, e.composto,
               e.exercicio_regressao_id, e.exercicio_progressao_id,
               m.nome AS modalidade
        FROM exercicios e
        JOIN modalidades m ON e.modalidade_id = m.id
    """
    joins = ""

    if objetivo:
        joins += " JOIN exercicio_objetivos eo ON eo.exercicio_id = e.id JOIN objetivos o ON eo.objetivo_id = o.id"
        conditions.append("LOWER(o.nome) LIKE ?")
        params.append(f"%{objetivo.lower()}%")

    if equipamento:
        joins += " JOIN exercicio_equipamentos ee ON ee.exercicio_id = e.id JOIN equipamentos eq ON ee.equipamento_id = eq.id"
        conditions.append("LOWER(eq.nome) LIKE ?")
        params.append(f"%{equipamento.lower()}%")

    if modalidade:
        conditions.append("LOWER(m.slug) = ?")
        params.append(_normalise_modalidade(modalidade))

    if nivel:
        conditions.append("e.nivel_dificuldade = ?")
        params.append(nivel.lower())

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = f"{base} {joins} {where} ORDER BY e.id"

    async with get_db() as conn:
        async with conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()

    results = []
    for row in rows:
        ex = dict(row)
        # Enriquecer com músculos, equipamentos, objetivos
        detail = await get_exercise_by_id(ex["id"])
        if detail:
            results.append(detail)
    return results


async def get_alternativas_progressoes(exercise_id: int) -> Dict[str, Any]:
    """RF-10: Recupera alternativas e progressão/regressão do banco."""
    async with get_db() as conn:
        # Alternativas
        async with conn.execute(
            """SELECT e.id, e.nome FROM exercicio_alternativas ea
               JOIN exercicios e ON ea.alternativa_id = e.id
               WHERE ea.exercicio_id = ?""",
            (exercise_id,),
        ) as cursor:
            alternativas = [{"id": r["id"], "nome": r["nome"]} for r in await cursor.fetchall()]

        # Regressão
        async with conn.execute(
            """SELECT e2.id, e2.nome FROM exercicios e1
               JOIN exercicios e2 ON e1.exercicio_regressao_id = e2.id
               WHERE e1.id = ?""",
            (exercise_id,),
        ) as cursor:
            row = await cursor.fetchone()
            regressao = {"id": row["id"], "nome": row["nome"]} if row else None

        # Progressão
        async with conn.execute(
            """SELECT e2.id, e2.nome FROM exercicios e1
               JOIN exercicios e2 ON e1.exercicio_progressao_id = e2.id
               WHERE e1.id = ?""",
            (exercise_id,),
        ) as cursor:
            row = await cursor.fetchone()
            progressao = {"id": row["id"], "nome": row["nome"]} if row else None

    return {
        "alternativas": alternativas,
        "regressao": regressao,
        "progressao": progressao,
    }


async def get_few_shot_treinos() -> List[Dict[str, Any]]:
    """Retorna treinos de exemplo para few-shot no prompt do LLM."""
    async with get_db() as conn:
        async with conn.execute(
            """SELECT t.id, t.nome, t.nivel_dificuldade AS nivel, t.duracao_min,
                      t.estrutura, m.nome AS modalidade, o.nome AS objetivo_principal
               FROM treinos t 
               JOIN modalidades m ON t.modalidade_id = m.id
               LEFT JOIN objetivos o ON t.objetivo_id = o.id
               LIMIT 5"""
        ) as cursor:
            treinos = [dict(r) for r in await cursor.fetchall()]

        for treino in treinos:
            async with conn.execute(
                """SELECT e.nome, te.series, te.repeticoes, te.descanso_seg, te.ordem, te.bloco
                   FROM treino_exercicios te JOIN exercicios e ON te.exercicio_id = e.id
                   WHERE te.treino_id = ? ORDER BY te.ordem""",
                (treino["id"],),
            ) as cursor:
                treino["exercicios"] = [dict(r) for r in await cursor.fetchall()]

    return treinos


def _normalise_modalidade(slug: str) -> str:
    """Normaliza slug de modalidade para comparação."""
    return (
        slug.lower()
        .replace("ç", "c")
        .replace("ã", "a")
        .replace("á", "a")
        .replace("é", "e")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace(" ", "_")
    )
