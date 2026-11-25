from pydantic import AliasChoices, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Education Platform API"
    app_name: str = "Education Platform API"
    environment: str = "local"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL Database
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "edu_db"
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/edu_db",
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
    )

    @computed_field
    @property
    def ASYNC_DATABASE_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Keycloak OIDC
    KEYCLOAK_SERVER_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "quizai"
    KEYCLOAK_CLIENT_ID: str = "quizai-web"
    KEYCLOAK_AUDIENCE: str = "quizai-api"
    KEYCLOAK_CLIENT_SECRET: str = ""

    @property
    def keycloak_issuer(self) -> str:
        return f"{self.KEYCLOAK_SERVER_URL.rstrip('/')}/realms/{self.KEYCLOAK_REALM}"

    @property
    def keycloak_jwks_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/certs"

    @property
    def keycloak_auth_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/auth"

    @property
    def keycloak_token_url(self) -> str:
        return f"{self.keycloak_issuer}/protocol/openid-connect/token"

    # Ollama Local LLM
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.2"

    # Redis Cache
    REDIS_URL: str = "redis://redis:6379/0"

    # RabbitMQ Broker
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

    # JWT Auth (local dev default; override in .env for production)
    JWT_SECRET_KEY: str = "change-me-local-only"
    JWT_EXPIRE_MINUTES: int = 60

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
    ]

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
