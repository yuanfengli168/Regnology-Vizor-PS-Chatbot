from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # Docs
    docs_folder_path: str = "./docs"

    # Admin
    admin_token: str = "change-me"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"

    # Database
    database_url: str = "sqlite:///./vizor_chat.db"

    # Cache
    cache_ttl: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
