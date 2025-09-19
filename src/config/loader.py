"""Configuration loading utilities."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
from .schemas import AppConfig, LLMConfig, TweeterConfig


def load_config_from_json(config_path: str = "env.json", bots_path: str = "bots.json") -> AppConfig:
    """Load configuration from JSON files.
    
    Args:
        config_path: Path to the main config JSON file
        bots_path: Path to the bots config JSON file
        
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
    
    # Load bots config if it exists
    bots_file = Path(bots_path)
    if bots_file.exists():
        with open(bots_file, 'r') as f:
            bots_data = json.load(f)
        
        # Add tweeter config to main config
        config_data["tweeter"] = bots_data
    
    return AppConfig(**config_data)

def load_config(config_path: str = "env.json", bots_path: str = "bots.json") -> AppConfig:
    """Load configuration with fallback strategy.
    
    1. Try loading from JSON files
    
    Args:
        config_path: Path to the main config JSON file
        bots_path: Path to the bots config JSON file
        
    Returns:
        AppConfig instance
        
    Raises:
        ValueError: If no valid configuration source is found
    """
    try:
        # Try JSON files first
        return load_config_from_json(config_path, bots_path)
    except (FileNotFoundError, ValueError) as json_error:
        raise ValueError(
            f"Could not load config from file '{config_path}' ({json_error}). "
            f"Please create a proper config file or set environment variables."
        )