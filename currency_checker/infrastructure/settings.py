from os import getenv
from pathlib import Path

from pydantic import BaseModel, BaseSettings


class LoggingSettings(BaseModel):
    config_path: Path = Path("./docker/plain-logging.yaml")
    level: str = 'INFO'


class PostgresSettings(BaseModel):
    host: str = 'postgres'
    port: int = 5432
    user: str
    password: str
    database: str
    ssl_mode: str = 'disable'


class RedisSettings(BaseModel):
    host: str
    port: int
    database: int


class SchedulerSettings(BaseModel):
    interval: int = 5
    queue: str = 'default'
    worker_count: int = 8


class Settings(BaseSettings):
    log: LoggingSettings
    postgres: PostgresSettings
    redis: RedisSettings

    binance_scheduler: SchedulerSettings
    coingeko_scheduler: SchedulerSettings

    api_metrics_port: int | None = None
    scheduler_metrics_port: int | None = None
    broker_metrics_port: int | None = None

    class Config:
        env_file_encoding = 'utf-8'
        env_file = getenv('ENV_PATH', 'conf/.env')
        env_nested_delimiter = '__'
