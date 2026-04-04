from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FrameForge API"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "components_ai"
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct:free"
    openrouter_fallback_models: str = "qwen/qwen3-coder:free,mistralai/mistral-7b-instruct:free,openrouter/free"
    openrouter_fallback_model: str = "openrouter/free"  # kept for backward compat
    frontend_url: str = "http://localhost:5173"
    max_context_messages: int = 10
    request_timeout_seconds: int = 60
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
