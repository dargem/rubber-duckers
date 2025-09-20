"""Configuration loading utilities."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .schemas import AppConfig, LLMConfig, UserConfig


def load_env_file(file_path: Path) -> Dict[str, str]:
    """Load environment variables from a .env file."""
    env_vars = {}
    
    if not file_path.exists():
        return env_vars
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove surrounding quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    env_vars[key] = value
                else:
                    print(f"Warning: Invalid line format in .env file at line {line_num}: {line}")
                    
    except Exception as e:
        print(f"Error reading .env file: {e}")
        
    return env_vars


def load_user_config_from_env(workspace_path: Path) -> Optional[UserConfig]:
    """Load user configuration from .env file."""
    env_file = workspace_path / ".env"
    
    if not env_file.exists():
        print("No .env file found - user config will be None")
        return None
    
    env_vars = load_env_file(env_file)
    
    # Extract user info from environment variables
    user_data = {}
    
    # Map environment variables to user config
    if 'NAME' in env_vars:
        user_data['display_name'] = env_vars['NAME']
    elif 'EMAIL' in env_vars:
        # Fallback to email username if no NAME specified
        email = env_vars['EMAIL']
        if '@' in email:
            user_data['display_name'] = email.split('@')[0]
        else:
            user_data['display_name'] = email
    
    if 'EMAIL' in env_vars:
        user_data['email'] = env_vars['EMAIL']
    
    if 'PASSWORD' in env_vars:
        user_data['password'] = env_vars['PASSWORD']
    
    if not user_data.get('display_name'):
        print("Warning: No NAME or EMAIL found in .env file - user config will be None")
        return None
    
    try:
        return UserConfig(**user_data)
    except Exception as e:
        print(f"Error creating user config from .env: {e}")
        return None


def load_config_from_json(config_path: str = "env.json") -> Dict[str, Any]:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to the main config JSON file
        
    Returns:
        Raw configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid JSON
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Validate that it has the required structure for our app
        if "llm" not in config_data:
            raise ValueError(f"Config file {config_path} does not contain required 'llm' section")
        
        return config_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")


def load_config(config_path: str = "env.json") -> AppConfig:
    """Load complete application configuration from JSON and .env files.
    
    Args:
        config_path: Path to the main config JSON file
        
    Returns:
        AppConfig instance with JSON config and user info from .env
        
    Raises:
        ValueError: If no valid configuration source is found
    """
    try:
        # Load main config from JSON
        json_data = load_config_from_json(config_path)
        
        # Load user config from .env file (if available)
        workspace_path = Path(config_path).parent
        user_config = load_user_config_from_env(workspace_path)
        
        # Combine configurations
        config_data = json_data.copy()
        if user_config:
            config_data['user'] = user_config.model_dump()
        
        # Create and validate the complete configuration
        return AppConfig(**config_data)
        
    except (FileNotFoundError, ValueError) as json_error:
        raise ValueError(
            f"Could not load config from file '{config_path}' ({json_error}). "
            f"Please create a proper config file or set environment variables."
        )