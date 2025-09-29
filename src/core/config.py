import os
from dataclasses import dataclass

from adaptix import Retort
from dynaconf import Dynaconf


@dataclass(slots=True)
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str
    driver: str = "postgresql+asyncpg"

    @property
    def dsn(self) -> str:
        """ "Сборка dsn для базы данных."""
        return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass(slots=True)
class LoggingConfig:
    level: str
    human_readable_logs: bool = True
    disabled_log_endpoints: list[str] = None
    logger_body_content_max_size: int = 1024


@dataclass(slots=True)
class BotConfig:
    token: str


@dataclass(slots=True)
class Config:
    database: DatabaseConfig
    logging: LoggingConfig
    bot: BotConfig


def get_config() -> Config:
    dynaconf = Dynaconf(
        settings_files=[os.getenv("CONFIG_FILE", "../config.toml")],
        envvar_prefix="MAV",
        load_dotenv=True,
        environments=True,
        default_env="default",
        merge_enabled=True,
        env_switcher="MAV_ENV",
    )
    retort = Retort()

    return retort.load(dynaconf, Config)


config: Config = get_config()
