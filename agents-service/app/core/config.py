import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    NVIDIA_API_KEY: str
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    ANALYZER_MODEL: str = "deepseek-ai/deepseek-v3.2"
    GENERATOR_MODEL: str = "qwen/qwen2.5-coder-32b-instruct"
    REVIEWER_MODEL: str = "deepseek-ai/deepseek-v3.2"

    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 16384

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    ORCHESTRATOR_HOST: str = "localhost"
    ORCHESTRATOR_PORT: int = 8001

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"),
        extra="ignore",
    )

    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    @property
    def orchestrator_callback_url(self) -> str:
        return f"http://{self.ORCHESTRATOR_HOST}:{self.ORCHESTRATOR_PORT}/spec"


settings = Settings()