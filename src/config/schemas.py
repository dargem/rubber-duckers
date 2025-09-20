"""Configuration schemas with validation."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class LLMConfig(BaseModel):
    """Configuration for LLM providers."""

    provider_type: str = Field(default="google")
    model_name: str = Field(default="gemini-2.5-flash-lite")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None)
    api_keys: List[str] = Field(min_items=1)
    max_requests_per_key: int = Field(default=15, ge=1, le=100)

    #TODO actually add these
    @field_validator("provider_type")
    def validate_provider_type(cls, v):
        allowed_providers = ["google", "openai", "anthropic", "ollama"]
        if v.lower() not in allowed_providers:
            raise ValueError(f"Provider type must be one of: {allowed_providers}")
        return v.lower()

    @field_validator("api_keys")
    def validate_api_keys(cls, v):
        if not v or any(not key.strip() for key in v):
            raise ValueError("All API keys must be non-empty")
        return [key.strip() for key in v]

    @field_validator("model_name")
    def validate_model_name(cls, v):
        allowed_models = [
            "gemini-2.5-pro",
            "gemini-2.5-flash", 
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-8b",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            # Add more models from different providers later
        ]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of: {allowed_models}")
        return v

    model_config = {"extra": "forbid"}


class UserConfig(BaseModel):
    """Configuration for the user account (from .env)."""
    
    display_name: str = Field(..., min_length=1)
    email: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)

    @field_validator("display_name")
    def validate_display_name(cls, v):
        if not v.strip():
            raise ValueError("Display name cannot be empty")
        return v.strip()

    model_config = {"extra": "forbid"}


class AppConfig(BaseModel):
    """Main application configuration."""

    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Core configurations - keep for rubber-duckers project
    llm: LLMConfig = Field(default_factory=LLMConfig)
    user: Optional[UserConfig] = Field(default=None)
    # Note: Bot accounts are now managed by AccountProvider, not config

    @field_validator("log_level")
    def validate_log_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    model_config = {"extra": "ignore"}  # Allow extra fields for AccountProvider migration
