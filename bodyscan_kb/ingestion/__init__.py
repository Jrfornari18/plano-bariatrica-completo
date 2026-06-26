"""BodyScan KB — Pacote de ingestão e recuperação RAG."""

from .pipeline import (
    ChunkRecuperado,
    RecomendacaoElegivel,
    ResultadoGate,
    avaliar_gatilhos,
    conectar,
    dividir_em_chunks,
    get_pool,
    ingerir_documento,
    ingerir_todos_documentos,
    montar_contexto_para_llm,
    recomendacoes_por_contexto,
    recuperar,
    recuperar_com_trigram,
)

__all__ = [
    "ChunkRecuperado",
    "RecomendacaoElegivel",
    "ResultadoGate",
    "avaliar_gatilhos",
    "conectar",
    "dividir_em_chunks",
    "get_pool",
    "ingerir_documento",
    "ingerir_todos_documentos",
    "montar_contexto_para_llm",
    "recomendacoes_por_contexto",
    "recuperar",
    "recuperar_com_trigram",
]
