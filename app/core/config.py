from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    APP_ENV: str = "dev"
    API_TITLE: str = "ai-docs-assistant"
    API_VERSION: str = "0.1.0"

    # OpenAI / models
    OPENAI_API_KEY: str = ""
    CHAT_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBED_DIM: int = 1536

    # DB
    DB_DSN: str = "postgresql+psycopg://docs:docs@localhost:5432/docs"

    # Auth
    API_KEY: Optional[str] = None

    # Retrieval / chunking
    TOP_K: int = 6
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150

    # Celery / Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_CONCURRENCY: int = 2


settings = Settings()
