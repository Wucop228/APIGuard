import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    ORCHESTRATOR_SERVICE_URL: str = "http://localhost:8001"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    GATEWAY_PORT: int = 8080
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"),
        extra="ignore"
    )


settings = Settings()
