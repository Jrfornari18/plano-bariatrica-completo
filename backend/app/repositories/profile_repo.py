"""
Repositório de perfis de usuário (RF-07).
"""
from typing import Optional, Dict, Any
from app.db.session import get_db
from app.models.profile import ProfileCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


async def create_profile(profile: ProfileCreate) -> int:
    """Cria um novo perfil e retorna o ID gerado."""
    async with get_db() as conn:
        cursor = await conn.execute(
            """INSERT INTO perfis_usuario
               (apelido, idade, sexo, altura_cm, peso_kg, imc, rcq, rca,
                nivel_experiencia, objetivo_id, frequencia_semanal,
                local_preferido, restricoes, equipamentos_disponiveis)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                profile.apelido,
                profile.idade,
                profile.sexo,
                profile.altura_cm,
                profile.peso_kg,
                profile.imc,
                profile.rcq,
                profile.rca,
                profile.nivel_experiencia,
                profile.objetivo_id,
                profile.frequencia_semanal,
                profile.local_preferido,
                profile.restricoes,
                profile.equipamentos_disponiveis,
            ),
        )
        profile_id = cursor.lastrowid
    logger.info("Perfil criado: id=%d", profile_id)
    return profile_id


async def get_profile(profile_id: int) -> Optional[Dict[str, Any]]:
    """Retorna um perfil pelo ID."""
    async with get_db() as conn:
        async with conn.execute(
            "SELECT * FROM perfis_usuario WHERE id = ?", (profile_id,)
        ) as cursor:
            row = await cursor.fetchone()
    if row:
        return dict(row)
    return None
