from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI RAG Backend Platform"
    app_env: str = "dev"
    debug: bool = True
    api_prefix: str = "/api/v1"

    mysql_dsn: str = "mysql+aiomysql://app:app@localhost:3306/ai_ops"
    mongodb_dsn: str = "mongodb://localhost:27017"
    mongodb_db: str = "ai_ops"
    redis_url: str = "redis://localhost:6379/0"
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    llm_provider: str = "mock"
    llm_api_base: str = ""
    llm_api_key: str = ""

    request_timeout_s: float = 15.0
    max_retries: int = 3
    circuit_breaker_failures: int = 3
    circuit_breaker_reset_timeout_s: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
