from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Database connection string for postgresql
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    database_url: Optional[str] = ''
    secret_key: Optional[str] = ''
    test_database_url: Optional[str] = ''
    algorithm: str = "HS256"


