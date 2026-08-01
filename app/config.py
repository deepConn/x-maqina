"""Configuration management for x-maqina"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # App Configuration
    app_name: str = "x-maqina"
    app_version: str = "1.0.0-alpha"
    environment: str = "development"
    debug: bool = True

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = True

    # Gemini API Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash"
    gemini_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/models"
    gemini_stream_timeout: int = 300
    gemini_max_tokens: int = 4096
    gemini_temperature: float = 0.7

    # Google Cloud Configuration
    gcp_project_id: Optional[str] = None
    gcp_region: str = "us-central1"

    # Database Configuration
    database_url: str = "postgresql://user:password@localhost:5432/xmaqina"
    database_pool_size: int = 20
    database_max_overflow: int = 40
    database_echo: bool = False

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600

    # Weaviate Configuration
    weaviate_url: str = "http://localhost:8080"
    weaviate_batch_size: int = 100

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Feature Flags
    enable_cybersecurity_engine: bool = True
    enable_financial_engine: bool = True
    enable_diagnostics_engine: bool = True
    enable_multi_agent_engine: bool = True
    enable_autonomous_engine: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
