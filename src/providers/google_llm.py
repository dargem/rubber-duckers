"""Google LLM provider implementation with key rotation."""

import asyncio
from typing import List
import logging
from langchain.schema import BaseMessage
from langchain_google_genai import GoogleGenerativeAI, ChatGoogleGenerativeAI
from pydantic import BaseModel
from .base import LLMProvider
from .api_key_manager import APIKeyManager


logger = logging.getLogger(__name__)


class GoogleLLMProvider(LLMProvider):
    """Google LLM provider with automatic API key rotation."""

    def __init__(
        self,
        api_key_manager: APIKeyManager,
        model_name: str = "gemini-2.5-flash-lite",
        temperature: float = 0.7,
        max_tokens: int = None,
    ):
        """Initialize the Google LLM provider.

        Args:
            api_key_manager: Manager for API key rotation
            model_name: The Google model to use
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response (None for unlimited)
        """
        self.api_key_manager = api_key_manager
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def invoke(self, messages: List[BaseMessage]) -> str:
        """Invoke the Google LLM with automatic key rotation.

        Args:
            messages: List of messages to send to the LLM

        Returns:
            The LLM response as a string

        Raises:
            Exception: If all API keys are exhausted or the request fails
        """
        max_retries = await self.api_key_manager.get_available_keys_count()
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Get a fresh API key for this request
                api_key = await self.api_key_manager.get_available_key()

                # Create LLM instance with current key
                llm_kwargs = {
                    "model": self.model_name,
                    "temperature": self.temperature,
                    "google_api_key": api_key,
                }
                if self.max_tokens:
                    llm_kwargs["max_tokens"] = self.max_tokens

                llm = GoogleGenerativeAI(**llm_kwargs)

                # Make the request in a thread to avoid blocking
                response = await asyncio.to_thread(llm.invoke, messages)

                logger.debug(
                    f"LLM request successful with key ending in ...{api_key[-4:]}"
                )
                return response.strip()

            except Exception as e:
                last_exception = e
                logger.warning(f"LLM request failed on attempt {attempt + 1}: {e}")

                # Mark the key as having an error
                if "api_key" in locals():
                    await self.api_key_manager.mark_key_error(api_key, e)

                # If this was the last attempt, raise the exception
                if attempt == max_retries - 1:
                    break

                # Wait a bit before retrying
                await asyncio.sleep(1)

        # If we get here, all retries failed
        raise Exception(f"All API keys failed. Last error: {last_exception}")

    async def schema_invoke(
        self, messages: List[BaseMessage], schema: BaseModel
    ) -> BaseModel:
        """Invoke the Google LLM with structured output and automatic key rotation.

        Args:
            messages: List of messages to send to the LLM
            schema: BaseModel schema for structured response

        Returns:
            The LLM response as the specified BaseModel schema

        Raises:
            Exception: If all API keys are exhausted or the request fails
        """
        max_retries = await self.api_key_manager.get_available_keys_count()
        last_exception = None

        for attempt in range(max_retries):
            try:
                # Get a fresh API key for this request
                api_key = await self.api_key_manager.get_available_key()

                # Create LLM instance with current key
                llm_kwargs = {
                    "model": self.model_name,
                    "temperature": self.temperature,
                    "google_api_key": api_key,
                }
                if self.max_tokens:
                    llm_kwargs["max_tokens"] = self.max_tokens

                # only chatgooglegenerativeai supports structured, generic doesn't
                llm = ChatGoogleGenerativeAI(**llm_kwargs)

                # Create structured LLM with schema
                structured_llm = llm.with_structured_output(schema)

                # Make the request in a thread to avoid blocking
                response = await asyncio.to_thread(structured_llm.invoke, messages)

                logger.debug(
                    f"Structured LLM request successful with key ending in ...{api_key[-4:]}"
                )
                return response

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Structured LLM request failed on attempt {attempt + 1}: {e}"
                )

                # Mark the key as having an error
                if "api_key" in locals():
                    await self.api_key_manager.mark_key_error(api_key, e)

                # If this was the last attempt, raise the exception
                if attempt == max_retries - 1:
                    break

                # Wait a bit before retrying
                await asyncio.sleep(1)

        # If we get here, all retries failed
        raise Exception(
            f"All API keys failed for structured output. Last error: {last_exception}"
        )

    async def health_check(self) -> bool:
        """Check if the provider is healthy and has available keys.

        Returns:
            True if the provider can handle requests, False otherwise
        """
        try:
            available_keys = await self.api_key_manager.get_available_keys_count()
            return available_keys > 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    async def get_available_keys_count(self) -> int:
        """Get the number of available API keys.

        Returns:
            Number of healthy, available API keys
        """
        return await self.api_key_manager.get_available_keys_count()
