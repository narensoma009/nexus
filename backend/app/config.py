from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://dev:devpassword@localhost:5432/att_platform"

    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER: str = "att-platform-files"

    ENTRA_TENANT_ID: str = ""
    ENTRA_CLIENT_ID: str = ""
    ENTRA_AUDIENCE: str = ""

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "att-account-platform"

    SECRET_KEY: str = "change-me"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"


settings = Settings()
