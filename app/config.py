from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str | None = None
    sqlalchemy_echo: bool = False
    media_upload_dir: str | None = None
    #: If > 0 and DATABASE_URL is SQLite, drop and recreate all tables on this interval (seconds).
    #: Destructive—use only for demos; default 0 disables.
    sqlite_auto_reset_seconds: int = Field(default=0, ge=0)
    #: After an auto-reset, run `seed()` (SQLite + interval only). Default on for demos.
    sqlite_auto_reset_seed: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
