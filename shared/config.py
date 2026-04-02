"""Shared configuration for all services."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Project
    project_name: str = "retail-intelligence"

    # PostgreSQL
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Services
    inference_service_url: str = "http://inference_service:8001"
    retrieval_service_url: str = "http://retrieval_service:8002"
    data_service_url: str = "http://data_service:8003"

    # Auth
    api_key: str

    @property
    def database_url(self) -> str:
        """PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
