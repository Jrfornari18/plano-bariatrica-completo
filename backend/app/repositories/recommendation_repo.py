"""
Repositório de recomendações: persistência e feedback (RF-06).
"""
import json
from typing import Optional, Dict, Any
from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)


async def save_recommendation(
    perfil_id: Optional[int],
    prompt: str,
    contexto_rag: Any,
    resposta: Any,
) -> int:
    """Persiste uma recomendação e retorna o ID gerado (RF-06)."""
    async with get_db() as conn:
        cursor = await conn.execute(
            """INSERT INTO recomendacoes (perfil_id, prompt, contexto_rag, resposta)
               VALUES (?, ?, ?, ?)""",
            (
                perfil_id,
                prompt,
                json.dumps(contexto_rag, ensure_ascii=False),
                json.dumps(resposta, ensure_ascii=False),
            ),
        )
        rec_id = cursor.lastrowid
    logger.info("Recomendação persistida: id=%d, perfil_id=%s", rec_id, perfil_id)
    return rec_id


async def update_feedback(rec_id: int, nota: int) -> bool:
    """Atualiza o feedback de uma recomendação (RF-06). Retorna True se encontrou o registro."""
    if nota < 1 or nota > 5:
        raise ValueError("Nota deve estar entre 1 e 5")
    async with get_db() as conn:
        cursor = await conn.execute(
            "UPDATE recomendacoes SET feedback = ? WHERE id = ?",
            (nota, rec_id),
        )
        updated = cursor.rowcount > 0
    if updated:
        logger.info("Feedback atualizado: rec_id=%d, nota=%d", rec_id, nota)
    else:
        logger.warning("Recomendação não encontrada para feedback: rec_id=%d", rec_id)
    return updated


async def get_recommendation(rec_id: int) -> Optional[Dict[str, Any]]:
    """Retorna uma recomendação pelo ID."""
    async with get_db() as conn:
        async with conn.execute(
            "SELECT * FROM recomendacoes WHERE id = ?", (rec_id,)
        ) as cursor:
            row = await cursor.fetchone()
    return dict(row) if row else None
