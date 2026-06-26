"""
Serviço de embeddings locais com FAISS (RF-01, RNF-08).
Usa sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2) — sem custo por chamada.
"""
import json
import os
import numpy as np
from typing import List, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_encoder = None
_faiss_index = None
_faiss_ids: List[int] = []


def _get_encoder():
    """Carrega o encoder de embeddings de forma lazy (singleton)."""
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Carregando modelo de embedding: %s", settings.embedding_model)
        _encoder = SentenceTransformer(settings.embedding_model)
        logger.info("Modelo de embedding carregado")
    return _encoder


def encode_text(text: str) -> np.ndarray:
    """Vetoriza um texto e retorna um array numpy normalizado."""
    encoder = _get_encoder()
    embedding = encoder.encode(text, normalize_embeddings=True)
    return embedding.astype(np.float32)


def encode_texts(texts: List[str]) -> np.ndarray:
    """Vetoriza uma lista de textos em lote."""
    encoder = _get_encoder()
    embeddings = encoder.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings.astype(np.float32)


def load_or_create_index() -> bool:
    """Carrega o índice FAISS do disco ou indica que precisa ser criado."""
    global _faiss_index, _faiss_ids
    import faiss

    index_path = settings.vector_index_path
    ids_path = settings.vector_ids_path

    if os.path.exists(index_path) and os.path.exists(ids_path):
        try:
            _faiss_index = faiss.read_index(index_path)
            with open(ids_path, "r") as f:
                _faiss_ids = json.load(f)
            logger.info("Índice FAISS carregado: %d vetores", _faiss_index.ntotal)
            return True
        except Exception as exc:
            logger.warning("Falha ao carregar índice FAISS: %s", exc)
    return False


def build_index(exercise_ids: List[int], documents: List[str]) -> None:
    """Constrói e persiste o índice FAISS a partir dos documentos (RF-01)."""
    global _faiss_index, _faiss_ids
    import faiss

    logger.info("Construindo índice FAISS para %d documentos...", len(documents))
    embeddings = encode_texts(documents)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner Product (vetores normalizados = cosine similarity)
    index.add(embeddings)

    os.makedirs(os.path.dirname(settings.vector_index_path), exist_ok=True)
    faiss.write_index(index, settings.vector_index_path)
    with open(settings.vector_ids_path, "w") as f:
        json.dump(exercise_ids, f)

    _faiss_index = index
    _faiss_ids = exercise_ids
    logger.info("Índice FAISS construído e salvo: %d vetores, dim=%d", index.ntotal, dim)


def search_similar(
    query: str,
    candidate_ids: Optional[List[int]] = None,
    top_k: int = 8,
) -> List[dict]:
    """
    RF-03: Busca semântica sobre os candidatos filtrados.
    Retorna lista de {exercicio_id, score} ordenada por score decrescente.
    """
    global _faiss_index, _faiss_ids

    if _faiss_index is None:
        if not load_or_create_index():
            logger.warning("Índice FAISS não disponível — retornando candidatos sem ranqueamento semântico")
            if candidate_ids:
                return [{"exercicio_id": eid, "score": 1.0} for eid in candidate_ids[:top_k]]
            return []

    query_vec = encode_text(query).reshape(1, -1)

    if candidate_ids is not None:
        # Filtrar apenas os candidatos permitidos
        allowed_set = set(candidate_ids)
        allowed_positions = [i for i, eid in enumerate(_faiss_ids) if eid in allowed_set]

        if not allowed_positions:
            return []

        # Busca nos vetores dos candidatos
        import faiss
        all_vectors = np.array([_faiss_index.reconstruct(i) for i in allowed_positions], dtype=np.float32)
        sub_index = faiss.IndexFlatIP(all_vectors.shape[1])
        sub_index.add(all_vectors)

        k = min(top_k, len(allowed_positions))
        scores, indices = sub_index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                original_pos = allowed_positions[idx]
                results.append({
                    "exercicio_id": _faiss_ids[original_pos],
                    "score": float(score),
                })
    else:
        k = min(top_k, _faiss_index.ntotal)
        scores, indices = _faiss_index.search(query_vec, k)
        results = [
            {"exercicio_id": _faiss_ids[idx], "score": float(score)}
            for score, idx in zip(scores[0], indices[0])
            if idx >= 0
        ]

    logger.info(
        "Recuperação semântica: %d resultados para query '%s...'",
        len(results),
        query[:50],
        extra={"rag_step": "retrieval", "top_k_count": len(results)},
    )
    return results
