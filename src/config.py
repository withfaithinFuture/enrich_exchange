from pathlib import Path
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(alias='POSTGRES_URL')

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        extra = "ignore"

