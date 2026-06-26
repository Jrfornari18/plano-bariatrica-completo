"""
Testes de validação anti-alucinação (RNF-04).
Critério de aceite: exercícios fora do contexto são rejeitados.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATABASE_PATH", "app/db/knowledge_base.db")

from app.services.recommendation_service import _validar_anti_alucinacao


def _make_treino(exercicio_ids: list) -> dict:
    """Helper para criar um dict de treino com os IDs fornecidos."""
    return {
        "treino": {
            "nome": "Teste",
            "modalidade": "funcional",
            "objetivo": "emagrecimento",
            "nivel": "iniciante",
            "duracao_min": 30,
            "estrutura": "circuito",
            "blocos": [
                {
                    "bloco": "principal",
                    "itens": [
                        {
                            "exercicio_id": eid,
                            "nome": f"Exercício {eid}",
                            "series": 3,
                            "repeticoes": "12",
                            "descanso_seg": 30,
                        }
                        for eid in exercicio_ids
                    ],
                }
            ],
        },
        "justificativa": "Teste",
        "contexto_recuperado": exercicio_ids,
    }


def test_validacao_passa_quando_todos_no_contexto():
    """RNF-04: Treino com todos os exercícios no contexto deve passar."""
    allowed = {1, 2, 3, 4, 5}
    treino = _make_treino([1, 2, 3])
    result = _validar_anti_alucinacao(treino, allowed)
    itens = result["treino"]["blocos"][0]["itens"]
    assert len(itens) == 3
    print("✓ Validação passa quando todos os exercícios estão no contexto")


def test_validacao_remove_exercicio_fora_do_contexto():
    """RNF-04: Exercício fora do contexto deve ser removido."""
    allowed = {1, 2, 3}
    treino = _make_treino([1, 2, 99])  # 99 não está no contexto
    result = _validar_anti_alucinacao(treino, allowed)
    itens = result["treino"]["blocos"][0]["itens"]
    ids_resultantes = [item["exercicio_id"] for item in itens]
    assert 99 not in ids_resultantes, "Exercício 99 deveria ter sido removido"
    assert 1 in ids_resultantes
    assert 2 in ids_resultantes
    print(f"✓ Exercício fora do contexto removido. Restantes: {ids_resultantes}")


def test_validacao_levanta_erro_quando_alucinacao_total():
    """RNF-04: Deve lançar ValueError quando todos os exercícios são alucinados."""
    allowed = {1, 2, 3}
    treino = _make_treino([99, 100, 101])  # Todos fora do contexto
    with pytest.raises(ValueError, match="alucinação total"):
        _validar_anti_alucinacao(treino, allowed)
    print("✓ ValueError levantado para alucinação total")


def test_validacao_preserva_blocos_validos():
    """RNF-04: Blocos com pelo menos um item válido devem ser preservados."""
    allowed = {1, 2, 5}
    treino = {
        "treino": {
            "nome": "Teste",
            "modalidade": "funcional",
            "objetivo": "emagrecimento",
            "nivel": "iniciante",
            "duracao_min": 30,
            "estrutura": "circuito",
            "blocos": [
                {
                    "bloco": "aquecimento",
                    "itens": [
                        {"exercicio_id": 1, "nome": "Ex1", "series": 1, "repeticoes": "60s", "descanso_seg": 15},
                        {"exercicio_id": 99, "nome": "Alucinado", "series": 1, "repeticoes": "60s", "descanso_seg": 15},
                    ],
                },
                {
                    "bloco": "principal",
                    "itens": [
                        {"exercicio_id": 100, "nome": "Alucinado2", "series": 3, "repeticoes": "12", "descanso_seg": 30},
                    ],
                },
            ],
        },
        "justificativa": "Teste",
        "contexto_recuperado": [1, 2, 5],
    }
    result = _validar_anti_alucinacao(treino, allowed)
    blocos = result["treino"]["blocos"]
    # Bloco aquecimento deve ter apenas o exercício 1
    assert len(blocos) == 1, f"Bloco 'principal' (todos alucinados) deveria ter sido removido. Blocos: {[b['bloco'] for b in blocos]}"
    assert blocos[0]["bloco"] == "aquecimento"
    assert len(blocos[0]["itens"]) == 1
    assert blocos[0]["itens"][0]["exercicio_id"] == 1
    print("✓ Blocos com alucinação parcial tratados corretamente")


def test_validacao_com_contexto_vazio():
    """RNF-04: Contexto vazio deve resultar em ValueError."""
    treino = _make_treino([1, 2, 3])
    with pytest.raises(ValueError):
        _validar_anti_alucinacao(treino, set())
    print("✓ Contexto vazio levanta ValueError")
