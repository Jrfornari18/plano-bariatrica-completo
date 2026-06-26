"""
Testes unitários — Serviço de Embeddings.
Verifica: provider mock, determinismo, similaridade cosseno, factory.
"""
import math
import pytest

from app.services.embedding import (
    EmbeddingProvider,
    MockEmbeddingProvider,
    get_embedding_provider,
)


class TestMockEmbeddingProvider:
    """Testes do MockEmbeddingProvider."""

    @pytest.fixture
    def provider(self):
        return MockEmbeddingProvider(dimension=64)

    @pytest.mark.asyncio
    async def test_embed_returns_correct_dimension(self, provider):
        vec = await provider.embed("teste de embedding")
        assert len(vec) == 64

    @pytest.mark.asyncio
    async def test_embed_is_deterministic(self, provider):
        """Mesmo texto deve retornar mesmo vetor."""
        text = "texto de teste determinístico"
        v1 = await provider.embed(text)
        v2 = await provider.embed(text)
        assert v1 == v2

    @pytest.mark.asyncio
    async def test_embed_different_texts_different_vectors(self, provider):
        v1 = await provider.embed("fisiologia")
        v2 = await provider.embed("nutrição")
        assert v1 != v2

    @pytest.mark.asyncio
    async def test_embed_returns_unit_vector(self, provider):
        vec = await provider.embed("normalização do vetor")
        norm = math.sqrt(sum(x * x for x in vec))
        assert abs(norm - 1.0) < 1e-6

    @pytest.mark.asyncio
    async def test_embed_batch(self, provider):
        texts = ["texto 1", "texto 2", "texto 3"]
        vecs = await provider.embed_batch(texts)
        assert len(vecs) == 3
        for v in vecs:
            assert len(v) == 64

    def test_model_version_format(self, provider):
        assert "mock" in provider.model_version
        assert "64" in provider.model_version

    def test_dimension_property(self, provider):
        assert provider.dimension == 64


class TestCosineSimilarity:
    """Testes da função de similaridade cosseno."""

    def test_identical_vectors_similarity_is_one(self):
        v = [1.0, 0.0, 0.0]
        assert abs(EmbeddingProvider.cosine_similarity(v, v) - 1.0) < 1e-6

    def test_orthogonal_vectors_similarity_is_zero(self):
        v1 = [1.0, 0.0]
        v2 = [0.0, 1.0]
        assert abs(EmbeddingProvider.cosine_similarity(v1, v2)) < 1e-6

    def test_opposite_vectors_similarity_is_minus_one(self):
        v1 = [1.0, 0.0]
        v2 = [-1.0, 0.0]
        assert abs(EmbeddingProvider.cosine_similarity(v1, v2) + 1.0) < 1e-6

    def test_zero_vector_returns_zero(self):
        v1 = [0.0, 0.0]
        v2 = [1.0, 0.0]
        assert EmbeddingProvider.cosine_similarity(v1, v2) == 0.0


class TestEmbeddingFactory:
    """Testes da factory de providers."""

    def test_get_embedding_provider_returns_provider(self):
        provider = get_embedding_provider()
        assert isinstance(provider, EmbeddingProvider)

    def test_get_embedding_provider_is_singleton(self):
        p1 = get_embedding_provider()
        p2 = get_embedding_provider()
        assert p1 is p2
