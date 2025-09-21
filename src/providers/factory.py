"""Factory for creating LLM providers based on configuration."""

from typing import Type
from ..config.schemas import LLMConfig
from .base import LLMProvider
from .google_llm import GoogleLLMProvider
from .api_key_manager import APIKeyManager


class LLMProviderFactory:
    """Factory for creating LLM providers based on configuration."""

    # Registry of provider types to their implementation classes
    _PROVIDERS = {
        "google": GoogleLLMProvider,
        # Future providers can be added here:
        # "openai": OpenAILLMProvider,
        # "anthropic": AnthropicLLMProvider,
        # "ollama": OllamaLLMProvider,
    }

    @classmethod
    def create_provider(
        cls, config: LLMConfig, api_key_manager: APIKeyManager
    ) -> LLMProvider:
        """Create an LLM provider based on configuration.

        Args:
            config: LLM configuration containing provider type and settings
            api_key_manager: API key manager for the provider

        Returns:
            LLMProvider: The configured provider instance

        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = config.provider_type.lower()

        if provider_type not in cls._PROVIDERS:
            available = ", ".join(cls._PROVIDERS.keys())
            raise ValueError(
                f"Unsupported provider type '{provider_type}'. Available: {available}"
            )

        provider_class = cls._PROVIDERS[provider_type]

        # Create provider with configuration
        return provider_class(
            api_key_manager=api_key_manager,
            model_name=config.model_name,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported provider types.

        Returns:
            List of supported provider type strings
        """
        return list(cls._PROVIDERS.keys())

    @classmethod
    def register_provider(
        cls, provider_type: str, provider_class: Type[LLMProvider]
    ) -> None:
        """Register a new provider type.

        Args:
            provider_type: String identifier for the provider
            provider_class: Provider class that implements LLMProvider

        Raises:
            ValueError: If provider_class doesn't implement LLMProvider
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(f"Provider class must implement LLMProvider interface")

        cls._PROVIDERS[provider_type.lower()] = provider_class

    @classmethod
    def is_provider_supported(cls, provider_type: str) -> bool:
        """Check if a provider type is supported.

        Args:
            provider_type: Provider type to check

        Returns:
            True if provider is supported, False otherwise
        """
        return provider_type.lower() in cls._PROVIDERS
