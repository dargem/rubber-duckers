"""Configuration management for rubber-duckers."""

from .schemas import AppConfig, LLMConfig, UserConfig
from .loader import load_config, load_config_from_json


# Import Container lazily to avoid circular imports
def get_container():
    """Get the container instance (lazy import to avoid circular dependencies)."""
    from .container import Container

    return Container


__all__ = [
    "AppConfig",
    "LLMConfig",
    "UserConfig",
    "load_config",
    "load_config_from_json",
    "get_container",
]
