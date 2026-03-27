"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    api_secret_key: str = "change-me"
    admin_api_key: str = "change-me-admin"

    # Optional external Presidio (if empty, built-in engine is used)
    presidio_external_url: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Limits
    max_file_size_mb: int = 50

    # NATS (for on-premise tunnel)
    nats_enabled: bool = False
    nats_url: str = "nats://localhost:4222"
    nats_token: str = ""
    nats_request_timeout: int = 120

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
