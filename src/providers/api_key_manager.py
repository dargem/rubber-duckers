"""API key management with rotation and health checking."""

import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging
from langchain_google_genai import GoogleGenerativeAI


logger = logging.getLogger(__name__)


@dataclass
class APIKeyStats:
    """Statistics and health information for an API key."""

    key: str
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_healthy: bool = True
    error_count: int = 0
    last_error: Optional[str] = None
    last_health_check: Optional[datetime] = None


class APIKeyManager:
    """Manages API key rotation, health checking, and usage tracking."""

    def __init__(self, api_keys: List[str], max_usage_per_key: int = 15):
        """Initialize the API key manager.

        Args:
            api_keys: List of API keys to manage
            max_usage_per_key: Maximum requests per key before rotation
        """
        if not api_keys:
            raise ValueError("At least one API key must be provided")

        self._keys = {key: APIKeyStats(key=key) for key in api_keys}
        self._max_usage = max_usage_per_key
        self._current_key_index = 0
        self._lock = asyncio.Lock()

    async def get_available_key(self) -> str:
        """Get the next available API key with load balancing.

        Returns:
            An available API key

        Raises:
            Exception: If no healthy keys are available
        """
        async with self._lock:
            # Find healthy keys under usage limit
            available_keys = [
                stats
                for stats in self._keys.values()
                if stats.is_healthy and stats.usage_count < self._max_usage
            ]

            if not available_keys:
                # Try to reset usage counters if all keys are at limit
                await self._reset_usage_counters()
                available_keys = [
                    stats for stats in self._keys.values() if stats.is_healthy
                ]

                if not available_keys:
                    raise Exception("No healthy API keys available")

            # Select key with lowest usage (round-robin with load balancing)
            selected_stats = min(available_keys, key=lambda x: x.usage_count)
            selected_stats.usage_count += 1
            selected_stats.last_used = datetime.now()

            logger.debug(
                f"Selected API key ending in ...{selected_stats.key[-4:]} "
                f"(usage: {selected_stats.usage_count}/{self._max_usage})"
            )

            return selected_stats.key

    async def mark_key_error(self, api_key: str, error: Exception) -> None:
        """Mark an API key as having encountered an error.

        Args:
            api_key: The API key that encountered an error
            error: The exception that occurred
        """
        if api_key in self._keys:
            stats = self._keys[api_key]
            stats.error_count += 1
            stats.last_error = str(error)

            # Mark as unhealthy if too many errors
            if stats.error_count >= 3:
                stats.is_healthy = False
                logger.warning(
                    f"API key ending in ...{api_key[-4:]} marked as unhealthy "
                    f"after {stats.error_count} errors"
                )

    async def is_key_healthy(self, api_key: str) -> bool:
        """Check if an API key is healthy.

        Args:
            api_key: The API key to check

        Returns:
            True if the key is healthy, False otherwise
        """
        if api_key not in self._keys:
            return False

        stats = self._keys[api_key]

        # Perform health check if it's been a while
        if (
            stats.last_health_check is None
            or datetime.now() - stats.last_health_check > timedelta(minutes=10)
        ):
            await self._health_check_key(api_key)

        return stats.is_healthy

    async def get_available_keys_count(self) -> int:
        """Get the number of healthy, available API keys.

        Returns:
            Number of healthy keys
        """
        return sum(1 for stats in self._keys.values() if stats.is_healthy)

    async def get_stats(self) -> Dict[str, Dict]:
        """Get statistics for all API keys.

        Returns:
            Dictionary mapping key suffixes to their stats
        """
        return {
            f"...{key[-4:]}": {
                "usage_count": stats.usage_count,
                "is_healthy": stats.is_healthy,
                "error_count": stats.error_count,
                "last_used": stats.last_used.isoformat() if stats.last_used else None,
                "last_error": stats.last_error,
            }
            for key, stats in self._keys.items()
        }

    async def _reset_usage_counters(self) -> None:
        """Reset usage counters for all keys."""
        for stats in self._keys.values():
            stats.usage_count = 0
        logger.info("Reset usage counters for all API keys")

    async def _health_check_key(self, api_key: str) -> None:
        """Perform a health check on a specific API key.

        Args:
            api_key: The API key to health check
        """
        try:
            # Simple health check with a minimal request
            llm = GoogleGenerativeAI(
                model="gemini-2.5-flash-lite", temperature=0.0, google_api_key=api_key
            )

            # Make a minimal test request
            await asyncio.to_thread(llm.invoke, "test")

            # If we get here, the key is healthy
            stats = self._keys[api_key]
            stats.is_healthy = True
            stats.last_health_check = datetime.now()
            stats.error_count = 0  # Reset error count on successful health check

            logger.debug(f"Health check passed for key ending in ...{api_key[-4:]}")

        except Exception as e:
            stats = self._keys[api_key]
            stats.is_healthy = False
            stats.last_health_check = datetime.now()
            stats.error_count += 1
            stats.last_error = str(e)

            logger.warning(
                f"Health check failed for key ending in ...{api_key[-4:]}: {e}"
            )

    async def refresh_unhealthy_keys(self) -> None:
        """Attempt to refresh all unhealthy keys by health checking them."""
        unhealthy_keys = [
            key for key, stats in self._keys.items() if not stats.is_healthy
        ]

        if unhealthy_keys:
            logger.info(f"Attempting to refresh {len(unhealthy_keys)} unhealthy keys")
            tasks = [self._health_check_key(key) for key in unhealthy_keys]
            await asyncio.gather(*tasks, return_exceptions=True)
