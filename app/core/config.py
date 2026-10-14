from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/deribit_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    DERIBIT_API_URL: str = "https://www.deribit.com/api/v2"
    PRICE_FETCH_INTERVAL_SECONDS: int = 60


settings = Settings()
