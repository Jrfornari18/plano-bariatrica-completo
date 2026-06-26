"""
Implementações de providers de LLM (RNF-07).
Configuráveis via variáveis de ambiente — sem hardcode de credenciais (RNF-02).
"""
import asyncio
import json
from typing import Optional
from app.services.llm.base import BaseLLMProvider, LLMError
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpenAICompatibleProvider(BaseLLMProvider):
    """
    Provider compatível com a API OpenAI (funciona com OpenAI, OpenAI-compatible endpoints, etc.).
    Credenciais lidas exclusivamente de variáveis de ambiente.
    """

    def __init__(self):
        self._api_key = settings.llm_api_key
        self._model = settings.llm_model or "gpt-4o-mini"
        self._base_url = settings.llm_base_url or None
        self._timeout = settings.llm_timeout_seconds

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.is_available():
            raise LLMError("LLM_API_KEY não configurada")

        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise LLMError("Pacote 'openai' não instalado. Execute: pip install openai")

        client_kwargs = {
            "api_key": self._api_key,
            "timeout": self._timeout,
        }
        if self._base_url:
            client_kwargs["base_url"] = self._base_url

        client = AsyncOpenAI(**client_kwargs)

        try:
            response = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            logger.info("LLM gerou resposta: %d chars", len(content or ""))
            return content or ""
        except Exception as exc:
            logger.error("Erro no provider LLM: %s", exc)
            raise LLMError(f"Erro na geração: {exc}") from exc


def get_llm_provider() -> BaseLLMProvider:
    """Factory: retorna o provider configurado via LLM_PROVIDER."""
    provider_name = settings.llm_provider.lower()
    if provider_name in ("openai", "openai_compatible", "anthropic"):
        return OpenAICompatibleProvider()
    # Default
    return OpenAICompatibleProvider()
