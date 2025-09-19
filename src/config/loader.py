"""Configuration loading utilities."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
from .schemas import AppConfig, LLMConfig


def load_config_from_json(config_path: str = "config.json") -> AppConfig:
    """Load configuration from a JSON file.
    
    Args:
        config_path: Path to the config JSON file
        
    Returns:
        AppConfig instance
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config is invalid
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    # Validate that it has the required structure for our app
    if "llm" not in config_data:
        raise ValueError(f"Config file {config_path} does not contain required 'llm' section")
    
    return AppConfig(**config_data)


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables.
    
    Environment variables:
    - ENVIRONMENT: App environment (default: development)
    - DEBUG: Debug mode (default: false)
    - LOG_LEVEL: Logging level (default: INFO)
    - GOOGLE_API_KEYS: Comma-separated list of Google API keys
    - LLM_MODEL: Model name (default: gemini-2.5-flash-lite)
    - LLM_TEMPERATURE: Temperature (default: 0.7)
    - LLM_MAX_TOKENS: Max tokens (default: None)
    - MAX_REQUESTS_PER_KEY: Max requests per key (default: 15)
    
    Returns:
        AppConfig instance
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Get Google API keys (required)
    api_keys_str = os.getenv("GOOGLE_API_KEYS")
    if not api_keys_str:
        raise ValueError("GOOGLE_API_KEYS environment variable is required")
    
    api_keys = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    if not api_keys:
        raise ValueError("At least one valid API key must be provided")
    
    # Build LLM config
    llm_config = LLMConfig(
        model_name=os.getenv("LLM_MODEL", "gemini-2.5-flash-lite"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS")) if os.getenv("LLM_MAX_TOKENS") else None,
        api_keys=api_keys,
        max_requests_per_key=int(os.getenv("MAX_REQUESTS_PER_KEY", "15")),
    )
    
    # Build app config
    return AppConfig(
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        llm=llm_config,
    )


def load_config(config_path: str = "env.json") -> AppConfig:
    """Load configuration with fallback strategy.
    
    1. Try loading from JSON file
    2. Fall back to environment variables
    3. Raise error if neither works
    
    Args:
        config_path: Path to the config JSON file
        
    Returns:
        AppConfig instance
        
    Raises:
        ValueError: If no valid configuration source is found
    """
    try:
        # Try JSON file first
        return load_config_from_json(config_path)
    except (FileNotFoundError, ValueError) as json_error:
        # Fall back to environment variables
        try:
            return load_config_from_env()
        except ValueError as env_error:
            raise ValueError(
                f"Could not load config from file '{config_path}' ({json_error}) or environment variables ({env_error}). "
                f"Please create a proper config file or set environment variables."
            )


def create_example_config(output_path: str = "env_example.json") -> None:
    """Create an example configuration file.
    
    Args:
        output_path: Where to save the example config
    """
    example_config = {
        "environment": "development",
        "debug": True,
        "log_level": "DEBUG",
        "llm": {
            "model_name": "gemini-2.5-flash-lite",
            "temperature": 0.7,
            "max_tokens": None,
            "api_keys": [
                "google-api-key-1-here",
                "google-api-key-2-here"
            ],
            "max_requests_per_key": 15
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print(f"Example config created at: {output_path}")
    print("Edit this file with your actual API keys and settings.")