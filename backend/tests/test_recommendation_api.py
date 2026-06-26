"""
Testes de integração do endpoint de recomendação (RF-05).
Critério de aceite: requisição válida → 200 com JSON do treino; inválida → 422.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATABASE_PATH", "app/db/knowledge_base.db")
os.environ.setdefault("VECTOR_INDEX_PATH", "app/db/faiss_index.bin")
os.environ.setdefault("VECTOR_IDS_PATH", "app/db/faiss_ids.json")
# Sem LLM_API_KEY — vai usar fallback por regras (degraded=True)
os.environ.setdefault("LLM_API_KEY", "")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """F0: GET /health deve retornar 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    print(f"✓ /health: {data}")


def test_recommendation_valid_request():
    """RF-05: Requisição válida deve retornar 200 com JSON do treino."""
    payload = {
        "intencao": "quero perder gordura treinando em casa, 30 minutos",
        "modalidades": ["funcional"],
        "nivel": "iniciante",
        "duracao_min": 30,
        "local": "casa",
        "equipamentos_disponiveis": ["Peso corporal"],
        "restricoes": [],
        "top_k": 5,
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200, f"Status {response.status_code}: {response.text}"
    data = response.json()

    # Verificar schema 8.2
    assert "recomendacao_id" in data
    assert "degraded" in data
    assert "treino" in data
    assert "justificativa" in data
    assert "contexto_recuperado" in data

    treino = data["treino"]
    assert "nome" in treino
    assert "blocos" in treino
    assert len(treino["blocos"]) > 0

    print(f"✓ Recomendação gerada: id={data['recomendacao_id']}, degraded={data['degraded']}")
    print(f"  Treino: {treino['nome']}")
    print(f"  Blocos: {[b['bloco'] for b in treino['blocos']]}")


def test_recommendation_invalid_request_missing_intencao():
    """RF-05: Requisição sem 'intencao' deve retornar 422."""
    payload = {
        "nivel": "iniciante",
        "duracao_min": 30,
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 422, f"Esperado 422, obtido {response.status_code}"
    print("✓ Requisição inválida retorna 422")


def test_recommendation_invalid_nivel():
    """RF-05: Nível inválido deve retornar 422."""
    payload = {
        "intencao": "treinar em casa",
        "nivel": "super_avancado",  # inválido
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 422
    print("✓ Nível inválido retorna 422")


def test_feedback_valid():
    """RF-06: Feedback válido (1-5) deve ser aceito."""
    # Primeiro criar uma recomendação
    payload = {
        "intencao": "treino de força para iniciantes",
        "nivel": "iniciante",
        "top_k": 3,
    }
    rec_response = client.post("/api/v1/recommendations", json=payload)
    assert rec_response.status_code == 200
    rec_id = rec_response.json()["recomendacao_id"]

    # Enviar feedback
    feedback_response = client.post(
        f"/api/v1/recommendations/{rec_id}/feedback",
        json={"nota": 4},
    )
    assert feedback_response.status_code == 200
    data = feedback_response.json()
    assert data["nota"] == 4
    assert data["recomendacao_id"] == rec_id
    print(f"✓ Feedback registrado: rec_id={rec_id}, nota=4")


def test_feedback_invalid_nota():
    """RF-06: Feedback com nota fora de 1-5 deve retornar 422."""
    response = client.post(
        "/api/v1/recommendations/1/feedback",
        json={"nota": 6},  # inválido
    )
    assert response.status_code == 422
    print("✓ Nota inválida (6) retorna 422")


def test_feedback_nota_zero():
    """RF-06: Feedback com nota 0 deve retornar 422."""
    response = client.post(
        "/api/v1/recommendations/1/feedback",
        json={"nota": 0},  # inválido
    )
    assert response.status_code == 422
    print("✓ Nota inválida (0) retorna 422")


def test_exercises_list():
    """RF-08: GET /api/v1/exercises deve retornar lista de exercícios."""
    response = client.get("/api/v1/exercises")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "exercicios" in data
    assert data["total"] == 40
    print(f"✓ Catálogo: {data['total']} exercícios")


def test_exercises_filter_by_modalidade():
    """RF-08: Filtro por modalidade deve retornar apenas exercícios da modalidade."""
    response = client.get("/api/v1/exercises?modalidade=funcional")
    assert response.status_code == 200
    data = response.json()
    for ex in data["exercicios"]:
        assert ex["modalidade"].lower() == "funcional", (
            f"Exercício '{ex['nome']}' não é funcional: {ex['modalidade']}"
        )
    print(f"✓ Filtro modalidade=funcional: {data['total']} exercícios")


def test_exercise_detail():
    """RF-08: GET /api/v1/exercises/{id} deve retornar detalhe com músculos e equipamentos."""
    response = client.get("/api/v1/exercises/1")
    assert response.status_code == 200
    data = response.json()
    assert "nome" in data
    assert "musculos" in data
    assert "equipamentos" in data
    assert "objetivos" in data
    print(f"✓ Detalhe exercício 1: {data['nome']}, músculos: {data['musculos'][:2]}")


def test_exercise_not_found():
    """RF-08: Exercício inexistente deve retornar 404."""
    response = client.get("/api/v1/exercises/9999")
    assert response.status_code == 404
    print("✓ Exercício inexistente retorna 404")


def test_profile_create_and_get():
    """RF-07: Perfil criado deve ser recuperável por ID."""
    profile_data = {
        "apelido": "Teste",
        "idade": 30,
        "sexo": "M",
        "altura_cm": 175.0,
        "peso_kg": 80.0,
        "imc": 26.1,
        "rcq": 0.85,
        "rca": 0.46,
        "nivel_experiencia": "iniciante",
        "local_preferido": "casa",
        "restricoes": "lombar",
        "equipamentos_disponiveis": "Peso corporal,Halteres",
    }
    # Criar
    create_response = client.post("/api/v1/profiles", json=profile_data)
    assert create_response.status_code == 201, f"Status {create_response.status_code}: {create_response.text}"
    created = create_response.json()
    profile_id = created["id"]
    assert created["apelido"] == "Teste"
    assert created["imc"] == 26.1

    # Recuperar
    get_response = client.get(f"/api/v1/profiles/{profile_id}")
    assert get_response.status_code == 200
    retrieved = get_response.json()
    assert retrieved["id"] == profile_id
    assert retrieved["apelido"] == "Teste"
    print(f"✓ Perfil criado e recuperado: id={profile_id}")


def test_profile_not_found():
    """RF-07: Perfil inexistente deve retornar 404."""
    response = client.get("/api/v1/profiles/99999")
    assert response.status_code == 404
    print("✓ Perfil inexistente retorna 404")


def test_recommendation_no_hallucination():
    """RNF-04: Exercícios no treino devem pertencer ao contexto recuperado."""
    payload = {
        "intencao": "treino funcional em casa para iniciantes",
        "nivel": "iniciante",
        "local": "casa",
        "top_k": 8,
    }
    response = client.post("/api/v1/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()

    contexto = set(data["contexto_recuperado"])
    for bloco in data["treino"]["blocos"]:
        for item in bloco["itens"]:
            assert item["exercicio_id"] in contexto, (
                f"Exercício id={item['exercicio_id']} ('{item['nome']}') "
                f"não está no contexto recuperado {contexto}"
            )
    print(f"✓ Anti-alucinação: todos os {sum(len(b['itens']) for b in data['treino']['blocos'])} exercícios estão no contexto")
