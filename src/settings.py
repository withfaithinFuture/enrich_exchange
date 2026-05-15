from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='POSTGRES_URL')
    BASE_BINANCE_URL: str = Field(env='BASE_BINANCE_URL')
    SYMBOLS_STR: str = Field(env='SYMBOLS_STR')
    SERVICE_NAME: str = Field(env='SERVICE_NAME')
    SERVICE_TYPE: str = Field(env='SERVICE_TYPE')
    KAFKA_URL: str = Field(env='KAFKA_URL')
    MAIN_TOPIC: str = Field(env='MAIN_TOPIC')
    DLQ_TOPIC: str = Field(env='DLQ_TOPIC')

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        extra = "ignore"


settings = Settings()