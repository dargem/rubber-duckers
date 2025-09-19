"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List
from langchain.schema import BaseMessage
from pydantic import BaseModel


class LLMProvider(ABC):
    """Abstract interface for LLM providers with automatic key rotation."""

    @abstractmethod
    async def invoke(self, messages: List[BaseMessage]) -> str:
        """Invoke the LLM with automatic key management.

        Args:
            messages: List of messages to send to the LLM

        Returns:
            The LLM response as a string

        Raises:
            Exception: If all API keys are exhausted or unhealthy
        """
        pass

    @abstractmethod
    async def schema_invoke(
        self, messages: List[BaseMessage], schema: BaseModel
    ) -> BaseModel:
        """Invoke the LLM with automatic key management.

        Args:
            messages: List of messages to send to the LLM
            schema: BaseModel for response formatting

        Returns:
            The LLM response as the BaseModel schema

        Raises:
            Exception: If all API keys are exhausted or unhealthy
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and has available keys.

        Returns:
            True if the provider can handle requests, False otherwise
        """
        pass

    @abstractmethod
    async def get_available_keys_count(self) -> int:
        """Get the number of available API keys.

        Returns:
            Number of healthy, available API keys
        """
        pass
