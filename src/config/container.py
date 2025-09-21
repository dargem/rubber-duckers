from src.providers import APIKeyManager, LLMProvider, LLMProviderFactory
from . import AppConfig
from typing import Dict, Any, Callable
from src.bots import BasicBot, ViralBot, NewsBot, ResponseBot
from src.tweeter import TweeterClient, QueryAgent
from src.account_providers import AccountProvider

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

        # Core providers
        self._providers[APIKeyManager] = lambda c: APIKeyManager(
            api_keys=config.llm.api_keys,
            max_usage_per_key=config.llm.max_requests_per_key,
        )

        # Use factory to create the appropriate LLM provider based on config
        self._providers[LLMProvider] = lambda c: LLMProviderFactory.create_provider(
            config=config.llm,
            api_key_manager=c.get(APIKeyManager),
        )

        # Account provider for managing multiple bot accounts
        self._providers[AccountProvider] = lambda c: AccountProvider()

        # Bots Here
        self._providers[BasicBot] = lambda c: BasicBot(
            llm_provider=c.get(LLMProvider)
        )

        self._providers[ViralBot] = lambda c: ViralBot(
            llm_provider=c.get(LLMProvider)
        )

        self._providers[NewsBot] = lambda c: NewsBot(
            llm_provider=c.get(LLMProvider),
            query_agent=c.get(QueryAgent)
        )

        self._providers[ResponseBot] = lambda c: ResponseBot(
            llm_provider=c.get(LLMProvider)
        )

        # API access - now uses AccountProvider to get current account
        self._providers[TweeterClient] = lambda c: self._create_tweeter_client(c)
        self._providers[QueryAgent] = lambda c: self._create_query_agent(c)

    def _create_tweeter_client(self, container):
        """Create TweeterClient with AccountProvider."""
        account_provider = container.get(AccountProvider)
        return TweeterClient(account_provider=account_provider)

    def _create_query_agent(self, container):
        """Create QueryAgent with AccountProvider."""
        account_provider = container.get(AccountProvider)
        return QueryAgent(account_provider=account_provider)


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
            provider = self.get(LLMProvider)
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
            provider = self.get(LLMProvider)
            if hasattr(provider.api_key_manager, "get_stats"):
                stats["api_key_manager"] = await provider.api_key_manager.get_stats()
            stats["llm_provider"] = {
                "available_keys": await provider.get_available_keys_count(),
                "provider_type": self._config.llm.provider_type,
            }
        except Exception as e:
            stats["llm_provider_error"] = str(e)

        return stats
