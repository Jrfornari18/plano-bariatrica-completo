"""Exporta todos os modelos ORM para uso pelo Alembic e pela aplicação."""
from app.models.l1_knowledge import (
    KnowledgeSource,
    KnowledgeChunk,
    Concept,
    ConceptRelation,
)
from app.models.l2_domain import (
    FisiologiaMarcador,
    TreinoExercicio,
    TreinoProtocolo,
    NutricaoAlimento,
    NutricaoProtocolo,
)
from app.models.l3_subject import (
    Usuario,
    PerfilFisiologicoSnapshot,
)
from app.models.l4_memory import (
    MemoriaEpisodica,
    MemoriaSemantica,
    MemoriaVinculoCrossDominio,
    ContextoSessao,
)
from app.models.l5_retrieval import RecuperacaoLog

__all__ = [
    "KnowledgeSource",
    "KnowledgeChunk",
    "Concept",
    "ConceptRelation",
    "FisiologiaMarcador",
    "TreinoExercicio",
    "TreinoProtocolo",
    "NutricaoAlimento",
    "NutricaoProtocolo",
    "Usuario",
    "PerfilFisiologicoSnapshot",
    "MemoriaEpisodica",
    "MemoriaSemantica",
    "MemoriaVinculoCrossDominio",
    "ContextoSessao",
    "RecuperacaoLog",
]
