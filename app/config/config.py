from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


dotenv_path = str(Path(__file__).resolve().parent.parent.parent / ".env")
load_dotenv(dotenv_path)


class DataBaseSettings(BaseSettings):
    url: str = "sqlite+aiosqlite:///./db.sqlite3"
    user: str = ""
    password: str = ""
    name: str = ""
    server: str = ""
    sqlalchemy_echo: bool = False


class Settings(BaseSettings):
    project_name: str = "Мониторинг самосвалов"
    version: str = "1.0"
    description: str = "Веб приложение для контроля работы самосвалов"
    api_prefix: str = "/api/v1"
    debug: bool = True

    db: DataBaseSettings = DataBaseSettings()

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_nested_delimiter="__"
    )


settings = Settings()
