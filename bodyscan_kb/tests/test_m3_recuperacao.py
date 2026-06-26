"""
test_m3_recuperacao.py — Testes para M3: Recuperação híbrida e camada de regras.

Critérios de aceite M3:
- RF-04: recuperar() retorna top-k filtrado por contexto e pelo gate de supervisão.
- RF-05: dado rca > 0.5 em perda_acelerada, a recomendação de pele é elegível.
- RF-08: chunks de supervisão não aparecem quando incluir_supervisao=False.
"""

import asyncio
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

os.environ.setdefault("EMBED_PROVIDER", "local")

from ingestion.pipeline import (
    avaliar_gatilhos,
    conectar,
    recomendacoes_por_contexto,
    recuperar,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bodyscan:bodyscan_secret@localhost:5432/bodyscan_kb",
)


def run_async(coro):
    """Helper para executar coroutines em testes síncronos."""
    return asyncio.get_event_loop().run_until_complete(coro)


@pytest.fixture(scope="session")
def db_pool():
    """Pool de conexão compartilhado para a sessão de testes."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    pool = loop.run_until_complete(conectar(DATABASE_URL))
    yield pool, loop
    loop.run_until_complete(pool.close())
    loop.close()


# -------------------------------------------------------------------------
# RF-04: Recuperação híbrida
# -------------------------------------------------------------------------
def test_recuperar_retorna_chunks(db_pool):
    """RF-04: recuperar() retorna resultados para consulta válida."""
    pool, loop = db_pool
    chunks = loop.run_until_complete(
        recuperar(pool, "lipólise e queima de gordura", k=3)
    )
    assert len(chunks) > 0, "Deve retornar pelo menos 1 chunk"
    for c in chunks:
        assert c.id is not None
        assert len(c.texto) > 0
        assert isinstance(c.distancia, float)
        assert isinstance(c.requer_supervisao, bool)
    print(f"  ✓ {len(chunks)} chunks retornados")


def test_recuperar_ordenado_por_distancia(db_pool):
    """RF-04: chunks retornados devem estar ordenados por distância crescente."""
    pool, loop = db_pool
    chunks = loop.run_until_complete(
        recuperar(pool, "proteína e massa magra", k=4)
    )
    if len(chunks) >= 2:
        for i in range(len(chunks) - 1):
            assert chunks[i].distancia <= chunks[i + 1].distancia, \
                "Chunks devem estar ordenados por distância crescente"
    print(f"  ✓ Ordenação por distância verificada ({len(chunks)} chunks)")


def test_recuperar_com_filtro_contexto(db_pool):
    """RF-04: filtro por contexto retorna resultados."""
    pool, loop = db_pool
    chunks_com_contexto = loop.run_until_complete(
        recuperar(pool, "pele e colágeno", contextos=["pele_redundante"], k=6)
    )
    chunks_sem_contexto = loop.run_until_complete(
        recuperar(pool, "pele e colágeno", k=6)
    )
    assert isinstance(chunks_com_contexto, list)
    assert isinstance(chunks_sem_contexto, list)
    print(f"  ✓ Com contexto: {len(chunks_com_contexto)}, sem contexto: {len(chunks_sem_contexto)}")


# -------------------------------------------------------------------------
# RF-08: Bloqueio de conteúdo com supervisão médica
# -------------------------------------------------------------------------
def test_sem_supervisao_exclui_chunks_restritos(db_pool):
    """RF-08: incluir_supervisao=False não retorna chunks requer_supervisao=True."""
    pool, loop = db_pool
    chunks = loop.run_until_complete(
        recuperar(pool, "micronutrientes pós-bariátrico", incluir_supervisao=False, k=10)
    )
    for c in chunks:
        assert not c.requer_supervisao, \
            f"Chunk {c.id} requer supervisão mas foi retornado com incluir_supervisao=False"
    print(f"  ✓ Nenhum chunk com supervisão retornado ({len(chunks)} chunks)")


def test_com_supervisao_pode_incluir_chunks_restritos(db_pool):
    """RF-08: incluir_supervisao=True pode retornar mais chunks."""
    pool, loop = db_pool
    chunks_sem = loop.run_until_complete(
        recuperar(pool, "monitorar micronutrientes", incluir_supervisao=False, k=10)
    )
    chunks_com = loop.run_until_complete(
        recuperar(pool, "monitorar micronutrientes", incluir_supervisao=True, k=10)
    )
    assert len(chunks_com) >= len(chunks_sem)
    print(f"  ✓ Com supervisão: {len(chunks_com)}, sem supervisão: {len(chunks_sem)}")


# -------------------------------------------------------------------------
# RF-05: Camada de regras — contexto + condição de métrica
# -------------------------------------------------------------------------
def test_recomendacao_pele_elegivel_com_rca_alto(db_pool):
    """RF-05: dado rca > 0.5 em perda_acelerada, recomendação de pele é elegível."""
    pool, loop = db_pool
    metricas = {"rca": 0.6}
    recs = loop.run_until_complete(
        recomendacoes_por_contexto(pool, "perda_acelerada", metricas)
    )
    slugs = [r.slug for r in recs]
    assert "cuidados_pele_perda_grande" in slugs, \
        f"Recomendação de pele deve ser elegível com rca=0.6. Slugs: {slugs}"
    print(f"  ✓ Recomendação de pele elegível com rca=0.6: {slugs}")


def test_recomendacao_pele_nao_elegivel_com_rca_baixo(db_pool):
    """RF-05: rca <= 0.5 em perda_acelerada NÃO torna recomendação de pele elegível."""
    pool, loop = db_pool
    metricas = {"rca": 0.4}
    recs = loop.run_until_complete(
        recomendacoes_por_contexto(pool, "perda_acelerada", metricas)
    )
    slugs = [r.slug for r in recs]
    assert "cuidados_pele_perda_grande" not in slugs, \
        f"Recomendação de pele NÃO deve ser elegível com rca=0.4. Slugs: {slugs}"
    print(f"  ✓ Recomendação de pele bloqueada com rca=0.4: {slugs}")


def test_recomendacoes_por_contexto_glp1(db_pool):
    """RF-05: contexto uso_glp1 retorna recomendação de proteína/massa magra."""
    pool, loop = db_pool
    recs = loop.run_until_complete(
        recomendacoes_por_contexto(pool, "uso_glp1")
    )
    slugs = [r.slug for r in recs]
    assert "priorizar_proteina_massa_magra" in slugs, \
        f"Recomendação de proteína deve ser elegível para uso_glp1. Slugs: {slugs}"
    print(f"  ✓ Recomendação de proteína elegível para uso_glp1: {slugs}")


def test_recomendacoes_por_contexto_pos_rygb(db_pool):
    """RF-05: contexto pos_rygb_0_12m retorna recomendação de micronutrientes."""
    pool, loop = db_pool
    recs = loop.run_until_complete(
        recomendacoes_por_contexto(pool, "pos_rygb_0_12m")
    )
    slugs = [r.slug for r in recs]
    assert "monitorar_micronutrientes_pos_bariatrico" in slugs, \
        f"Recomendação de micronutrientes deve ser elegível para pos_rygb_0_12m. Slugs: {slugs}"
    print(f"  ✓ Recomendação de micronutrientes elegível para pos_rygb: {slugs}")


# -------------------------------------------------------------------------
# RF-07: Detecção de gatilhos de escalonamento
# -------------------------------------------------------------------------
def test_gatilho_transtorno_alimentar(db_pool):
    """RF-07: entrada com termos de transtorno alimentar dispara escalonamento."""
    pool, loop = db_pool
    resultado = loop.run_until_complete(
        avaliar_gatilhos(pool, "quero parar de comer completamente")
    )
    assert resultado.bloqueado, "Deve bloquear entrada com sinal de transtorno alimentar"
    assert resultado.tipo_alerta is not None
    print(f"  ✓ Gatilho disparado: {resultado.tipo_alerta} → {resultado.acao}")


def test_gatilho_meta_insegura(db_pool):
    """RF-07: meta de perda insegura dispara escalonamento."""
    pool, loop = db_pool
    resultado = loop.run_until_complete(
        avaliar_gatilhos(pool, "quero perder 10kg em uma semana")
    )
    assert resultado.bloqueado, "Deve bloquear meta de perda insegura"
    print(f"  ✓ Meta insegura bloqueada: {resultado.tipo_alerta}")


def test_gatilho_gestacao(db_pool):
    """RF-07: entrada de gestante dispara bloqueio."""
    pool, loop = db_pool
    resultado = loop.run_until_complete(
        avaliar_gatilhos(pool, "estou grávida e quero emagrecer")
    )
    assert resultado.bloqueado, "Deve bloquear recomendação para gestante"
    assert resultado.acao == "bloquear"
    print(f"  ✓ Gestação bloqueada: acao={resultado.acao}")


def test_sem_gatilho_para_consulta_normal(db_pool):
    """RF-07: consulta normal não dispara escalonamento."""
    pool, loop = db_pool
    resultado = loop.run_until_complete(
        avaliar_gatilhos(pool, "como a lipólise funciona no tecido adiposo?")
    )
    assert not resultado.bloqueado, "Consulta normal não deve disparar escalonamento"
    assert resultado.tipo_alerta is None
    print(f"  ✓ Consulta normal: sem escalonamento")


if __name__ == "__main__":
    import subprocess
    subprocess.run(["python3", "-m", "pytest", __file__, "-v", "-s"])
