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
    keycloak_issuer: str = Field(
        default="http://localhost:8080/realms/quizai",
        validation_alias=AliasChoices("KEYCLOAK_ISSUER", "keycloak_issuer"),
    )
    keycloak_jwks_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KEYCLOAK_JWKS_URL", "keycloak_jwks_url"),
    )
    keycloak_audience: str = Field(
        default="quizai-api",
        validation_alias=AliasChoices("KEYCLOAK_AUDIENCE", "keycloak_audience"),
    )
    keycloak_client_id: str = Field(
        default="quizai-web",
        validation_alias=AliasChoices("KEYCLOAK_CLIENT_ID", "keycloak_client_id"),
    )

    @property
    def jwks_url(self) -> str:
        return self.keycloak_jwks_url or f"{self.keycloak_issuer.rstrip('/')}/protocol/openid-connect/certs"

    @property
    def keycloak_auth_url(self) -> str:
        return f"{self.keycloak_issuer.rstrip('/')}/protocol/openid-connect/auth"

    @property
    def keycloak_token_url(self) -> str:
        return f"{self.keycloak_issuer.rstrip('/')}/protocol/openid-connect/token"

    # Ollama Local LLM
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_DEFAULT_MODEL: str = "llama3.2"

    # Redis Cache
    REDIS_URL: str = "redis://redis:6379/0"

    # RabbitMQ Broker
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"

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
