"""
Testes do filtro estruturado SQL (RF-02).
Critério de aceite: dado perfil com restrição 'lombar' e sem equipamento de academia,
o conjunto de candidatos não contém levantamento-terra nem exercícios requer_academia=1.
"""
import pytest
import asyncio
import os
import sys

# Configurar path e banco de teste
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATABASE_PATH", "app/db/knowledge_base.db")

from app.repositories.exercise_repo import filtrar_candidatos, _normalise_modalidade


@pytest.mark.asyncio
async def test_filtro_exclui_contraindicacao_lombar():
    """RF-02: Exercícios com contraindicação lombar devem ser excluídos."""
    candidatos = await filtrar_candidatos(
        excluir_contraindicacoes=["lombar"]
    )
    ids = [c["id"] for c in candidatos]
    nomes = [c["nome"] for c in candidatos]

    # Levantamento terra tem contraindicação lombar
    assert all("levantamento" not in n.lower() for n in nomes), (
        f"Levantamento terra não deveria estar nos candidatos. Encontrado: {nomes}"
    )
    print(f"✓ Filtro lombar: {len(candidatos)} candidatos (sem levantamento terra)")


@pytest.mark.asyncio
async def test_filtro_exclui_academia_quando_local_casa():
    """RF-02: Exercícios que requerem academia devem ser excluídos quando local='casa'."""
    candidatos = await filtrar_candidatos(local="casa")
    ids = [c["id"] for c in candidatos]

    # Verificar que nenhum exercício requer academia
    from app.db.session import get_db
    async with get_db() as conn:
        for cid in ids:
            async with conn.execute(
                """SELECT COUNT(*) as cnt FROM exercicio_equipamentos ee
                   JOIN equipamentos eq ON ee.equipamento_id = eq.id
                   WHERE ee.exercicio_id = ? AND eq.requer_academia = 1""",
                (cid,),
            ) as cursor:
                row = await cursor.fetchone()
                assert row["cnt"] == 0, (
                    f"Exercício id={cid} requer academia mas foi incluído no filtro 'casa'"
                )
    print(f"✓ Filtro local=casa: {len(candidatos)} candidatos (nenhum requer academia)")


@pytest.mark.asyncio
async def test_filtro_por_modalidade():
    """RF-02: Filtro por modalidade retorna apenas exercícios da modalidade solicitada."""
    candidatos = await filtrar_candidatos(modalidades=["funcional"])
    assert len(candidatos) > 0, "Deve haver exercícios funcionais"
    for c in candidatos:
        assert c["modalidade_slug"] == "funcional", (
            f"Exercício '{c['nome']}' não é funcional: {c['modalidade_slug']}"
        )
    print(f"✓ Filtro modalidade=funcional: {len(candidatos)} candidatos")


@pytest.mark.asyncio
async def test_filtro_por_nivel_iniciante():
    """RF-02: Filtro por nível iniciante não deve incluir exercícios avançados."""
    candidatos = await filtrar_candidatos(nivel="iniciante")
    assert len(candidatos) > 0
    for c in candidatos:
        assert c["nivel_dificuldade"] in ("iniciante",), (
            f"Exercício '{c['nome']}' é nível '{c['nivel_dificuldade']}' mas filtro era iniciante"
        )
    print(f"✓ Filtro nivel=iniciante: {len(candidatos)} candidatos")


@pytest.mark.asyncio
async def test_filtro_combinado_lombar_e_casa():
    """RF-02: Filtro combinado (lombar + casa) deve excluir ambos os grupos."""
    candidatos = await filtrar_candidatos(
        excluir_contraindicacoes=["lombar"],
        local="casa",
    )
    nomes = [c["nome"] for c in candidatos]
    assert all("levantamento" not in n.lower() for n in nomes)
    print(f"✓ Filtro combinado lombar+casa: {len(candidatos)} candidatos")


def test_normalise_modalidade():
    """Testa a normalização de slugs de modalidade."""
    assert _normalise_modalidade("Musculação") == "musculacao"
    assert _normalise_modalidade("Aeróbico") == "aerobico"
    assert _normalise_modalidade("funcional") == "funcional"
    print("✓ Normalização de modalidade OK")
