from abc import ABC, abstractmethod
from src.providers import LLMProvider

class Bot(ABC):
    """Abstract interface for bots"""

    @abstractmethod
    def __init__(self, llm_provider: LLMProvider):
        """
        Args:
            LLM Provider interface for llms
        """
        pass

    @abstractmethod
    async def run_bot(self) -> str:
        """
        Runs the bot, returning its response

        Returns:
            LLM response as a string
        """
        pass