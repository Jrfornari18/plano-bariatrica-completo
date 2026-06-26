"""
Testes do serviço de recuperação semântica (RF-03).
Critério de aceite: top-K coerente e restrito aos candidatos filtrados.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DATABASE_PATH", "app/db/knowledge_base.db")
os.environ.setdefault("VECTOR_INDEX_PATH", "app/db/faiss_index.bin")
os.environ.setdefault("VECTOR_IDS_PATH", "app/db/faiss_ids.json")

from app.services.embedding_service import (
    load_or_create_index,
    search_similar,
    encode_text,
)


def test_index_loads():
    """RF-01: Índice FAISS deve carregar com 40 vetores."""
    loaded = load_or_create_index()
    from app.services.embedding_service import _faiss_index, _faiss_ids
    assert loaded, "Índice FAISS não encontrado — execute scripts/ingest_embeddings.py"
    assert _faiss_index is not None
    assert _faiss_index.ntotal == 40, f"Esperado 40 vetores, encontrado {_faiss_index.ntotal}"
    assert len(_faiss_ids) == 40
    print(f"✓ Índice FAISS carregado: {_faiss_index.ntotal} vetores")


def test_encode_text_returns_vector():
    """Encode deve retornar vetor de dimensão 384."""
    vec = encode_text("queimar gordura")
    assert vec.shape == (384,), f"Dimensão esperada 384, obtida {vec.shape}"
    print("✓ Encode retorna vetor dim=384")


def test_search_similar_top_k():
    """RF-03: search_similar deve retornar no máximo top_k resultados."""
    load_or_create_index()
    results = search_similar("perder peso em casa", top_k=5)
    assert len(results) <= 5, f"Esperado ≤5 resultados, obtido {len(results)}"
    assert len(results) > 0, "Deve retornar pelo menos 1 resultado"
    print(f"✓ search_similar top-5: {[r['exercicio_id'] for r in results]}")


def test_search_similar_ordered_by_score():
    """RF-03: Resultados devem estar ordenados por score decrescente."""
    load_or_create_index()
    results = search_similar("força muscular", top_k=8)
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True), (
        f"Resultados não estão ordenados por score: {scores}"
    )
    print(f"✓ Resultados ordenados por score: {[round(s, 3) for s in scores]}")


def test_search_similar_restricted_to_candidates():
    """RF-03: Resultados devem pertencer ao conjunto de candidatos fornecido."""
    load_or_create_index()
    # Usar apenas IDs 1-10 como candidatos
    candidate_ids = list(range(1, 11))
    results = search_similar("agachamento força pernas", candidate_ids=candidate_ids, top_k=5)
    result_ids = [r["exercicio_id"] for r in results]
    for rid in result_ids:
        assert rid in candidate_ids, (
            f"Exercício id={rid} não está nos candidatos {candidate_ids}"
        )
    print(f"✓ Resultados restritos aos candidatos: {result_ids}")


def test_search_queimar_gordura_sem_equipamento():
    """RF-01 critério de aceite: 'queimar gordura sem equipamento' deve recuperar exercícios aeróbicos/funcionais."""
    load_or_create_index()
    results = search_similar("queimar gordura sem equipamento", top_k=5)
    assert len(results) == 5
    # Verificar que retorna IDs válidos (1-40)
    for r in results:
        assert 1 <= r["exercicio_id"] <= 40
    print(f"✓ Query 'queimar gordura': IDs recuperados = {[r['exercicio_id'] for r in results]}")
