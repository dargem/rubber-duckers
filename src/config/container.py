from src.providers import APIKeyManager
from . import AppConfig
from typing import Dict, Any, Callable
from src.providers import GoogleLLMProvider

class Container:
    """Dependency injection container using a registry of providers."""

    def __init__(self):
        self._config: AppConfig | None = None
        self._instances: Dict[Any, Any] = {}
        self._providers: Dict[Any, Callable[["Container"], Any]] = {}

    async def set_config(self, config: AppConfig) -> None:
        """Set the app config and register providers."""
        self._config = config
        self._instances.clear()
        self._providers.clear()

        # Core providers for rubber-duckers
        self._providers[APIKeyManager] = lambda c: APIKeyManager(
            api_keys=config.llm.api_keys,
            max_usage_per_key=config.llm.max_requests_per_key,
        )

        self._providers[GoogleLLMProvider] = lambda c: GoogleLLMProvider(
            api_key_manager=c.get(APIKeyManager),
            model_name=config.llm.model_name,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
        )

        # TODO: Add future providers as needed
        # self._providers[TwooterClient] = lambda c: TwooterClient(...)
        # self._providers[DatabaseManager] = lambda c: DatabaseManager(...)
        
        # Commented out - these were from another project
        # Factories depend on stats needs KG calls
        #stats = await self.get_stats()
        """
        self._providers[IngestionWorkflowFactory] = lambda c: IngestionWorkflowFactory(
            c.get(GoogleLLMProvider)
            if config.environment != "testing"
            else c.get(MockLLMProvider),
            c.get(KnowledgeGraphManager),
        )

        self._providers[TranslationWorkflowFactory] = (
            lambda c: TranslationWorkflowFactory(
                c.get(GoogleLLMProvider)
                if config.environment != "testing"
                else c.get(MockLLMProvider),
                c.get(KnowledgeGraphManager),
                stats["config"]["max_feedback_loops"],
            )
        )
        """


    def get(self, key: Any):
        """Generic resolver with caching."""
        if key in self._instances:
            return self._instances[key]
        if key not in self._providers:
            raise ValueError(f"No provider registered for {key}")
        instance = self._providers[key](self)
        self._instances[key] = instance
        return instance
    
    async def health_check(self):
        """Check health of core services."""
        results = {}
        try:
            provider = self.get(GoogleLLMProvider)
            results["llm_provider"] = await provider.health_check()
        except Exception as e:
            results["llm_provider"] = False
            results["llm_provider_error"] = str(e)

        # TODO: Add other health checks as services are added
        # try:
        #     twooter = self.get(TwooterClient)  
        #     results["twooter"] = await twooter.health_check()
        # except Exception as e:
        #     results["twooter"] = False
        #     results["twooter_error"] = str(e)

        return results

    async def get_stats(self):
        """Get statistics for monitoring and debugging."""
        stats = {
            "environment": self._config.environment,
            "config": {
                "llm_model": self._config.llm.model_name,
                "llm_temperature": self._config.llm.temperature,
                # "max_feedback_loops": self._config.workflow.max_feedback_loops,  # commented out - not needed yet
            },
        }

        try:
            provider = self.get(GoogleLLMProvider)
            if hasattr(provider.api_key_manager, "get_stats"):
                stats["api_key_manager"] = await provider.api_key_manager.get_stats()
            stats["llm_provider"] = {
                "available_keys": await provider.get_available_keys_count()
            }
        except Exception as e:
            stats["llm_provider_error"] = str(e)

        return stats
