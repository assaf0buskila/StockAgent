"""
Configuration management for the Financial AI Agent.

Uses pydantic-settings for environment variable management.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    
    Attributes:
        LLM_BASE_URL: Base URL for the Ollama LLM service
        LLM_MODEL_NAME: Name of the LLM model to use
        LLM_TIMEOUT: Timeout in seconds for LLM requests
        NEWS_API_KEY: Optional API key for premium news services
        ENVIRONMENT: Current environment (development, production, etc.)
        CORS_ORIGINS: Allowed CORS origins for API access
    """
    
    # LLM Configuration
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL_NAME: str = 'llama3.2:3b'
    LLM_TIMEOUT: int = 240
  # Increased timeout for slower models
    
    # News API Configuration (optional)
    NEWS_API_KEY: Optional[str] = None
    
    # Application Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"
    
    # Stock Data Configuration
    PRICE_HISTORY_PERIOD: str = "1mo"  # Default period for price history
    NEWS_LIMIT: int = 5  # Default number of news articles to fetch
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"


# Global settings instance
settings = Settings()


# Print configuration on import (only in development)
if settings.DEBUG:
    print("\n" + "=" * 50)
    print("⚙️  Configuration Loaded")
    print("=" * 50)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"LLM URL: {settings.LLM_BASE_URL}")
    print(f"LLM Model: {settings.LLM_MODEL_NAME}")
    print(f"LLM Timeout: {settings.LLM_TIMEOUT}s")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"CORS Origins: {settings.CORS_ORIGINS}")
    print("=" * 50 + "\n")