from dotenv import load_dotenv
load_dotenv()

import os
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    postgres_url: PostgresDsn = Field(env='POSTGRES_URL')
    BASE_URL = os.getenv('BASE_BINANCE_URL')
    SYMBOLS_STR = os.getenv('SYMBOLS_STR')

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        extra = "ignore"
