import pathlib

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    # DATABASE_URL: SecretStr

    REDIS_HOST: SecretStr
    REDIS_PORT: int

    POSTGRES_HOST: SecretStr
    POSTGRES_PORT: int
    POSTGRES_DB: SecretStr
    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr

    OPENWEATHERMAP_API: SecretStr
    FOURSQUARE_API: SecretStr

    model_config = SettingsConfigDict(env_file=f"{pathlib.Path(__file__).parent.resolve()}/.env",
                                      env_file_encoding="utf-8",
                                      extra="ignore")


config = Settings()
