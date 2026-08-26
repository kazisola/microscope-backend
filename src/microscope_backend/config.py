from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "MicroScope"
    envrionment: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="UTF-8",
        extra="ignore"
    )

    database_url: str

# Create a Settings instance so Settings() is constructed once per process
@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore

settings = get_settings()