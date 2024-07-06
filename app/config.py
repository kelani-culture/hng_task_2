from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Database connection string for postgresql
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )
    database_url: str
    secret_key: str
    algorithm: str = "HS256"


