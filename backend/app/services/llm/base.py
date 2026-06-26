"""
Interface abstrata do provider de LLM (RNF-07).
Trocável por variável de ambiente sem alterar código de negócio.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMError(Exception):
    """Erro genérico do provider de LLM."""
    pass


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Gera texto a partir de prompts de sistema e usuário."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provider está configurado e disponível."""
        ...
