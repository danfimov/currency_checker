from os import getenv
from pathlib import Path

from pydantic import BaseModel, BaseSettings


class LoggingSettings(BaseModel):
    config_path: Path = Path("./docker/plain-logging.yaml")
    level: str = 'INFO'


class PostgresSettings(BaseModel):
    host: str = 'postgres'
    port: int = 5432
    user: str = 'currency_checker'
    password: str = 'currency_checker'
    database: str = 'currency_checker'
    ssl_mode: str = 'disable'


class RedisSettings(BaseModel):
    host: str = 'redis'
    port: int = 6379
    database: int = 0


class SchedulerSettings(BaseModel):
    interval: int = 5
    queue: str = 'default'
    worker_count: int = 8


class Settings(BaseSettings):
    log: LoggingSettings = LoggingSettings()
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()

    binance_scheduler: SchedulerSettings = SchedulerSettings()
    coingeko_scheduler: SchedulerSettings = SchedulerSettings()

    class Config:
        env_file_encoding = 'utf-8'
        env_file = getenv('ENV_PATH', 'conf/.env')
        env_nested_delimiter = '__'
