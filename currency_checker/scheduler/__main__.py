import asyncio
import signal
from datetime import datetime
from logging import getLogger
from types import FrameType

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.blocking import BlockingScheduler

from currency_checker.domain.storages.accounts import AbstractAccountStorage, PostgresAccountStorage
from currency_checker.infrastructure.logging import configure_logging
from currency_checker.infrastructure.settings import Settings
from currency_checker.scheduler.exceptions import ConfigurationException
from currency_checker.scheduler.jobs import (
    binance_get_currency_rates,
    binance_get_currency_rates_by_websocket,
    coingeko_get_currency_rates,
)
from currency_checker.scheduler.utils import run_metrics_server


logger = getLogger(__name__)
scheduler: BlockingScheduler | None = None
account_storage: AbstractAccountStorage | None = None


def sigterm_handler(_signal: int, _frame: FrameType | None) -> None:
    logger.debug('SIGTERM received, stopping workers...')
    if scheduler is not None:
        scheduler.shutdown()
    logger.debug('Workers stopped')
    exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)


def scheduled_task_binance() -> None:
    binance_get_currency_rates.send()


def scheduled_task_coingeko() -> None:
    if account_storage is None:
        raise ConfigurationException("Account storage is not initialized")
    account = account_storage.get_active_account('coingeko')
    coingeko_get_currency_rates.send(account.token)


def scheduled_task_binance_by_websocket() -> None:
    binance_get_currency_rates_by_websocket.send()


if __name__ == "__main__":
    settings = Settings()
    configure_logging(
        path_to_log_config=settings.log.config_path,
        root_level=settings.log.level,
    )
    metrics_server = run_metrics_server(settings.scheduler_metrics_port)

    job_stores = {
        'default': RedisJobStore(
            db=settings.redis.database,
            host=settings.redis.host,
            port=settings.redis.port,
        )
    }
    scheduler = BlockingScheduler(jobstores=job_stores)

    if settings.enable_websocket_binance_client:
        scheduler.add_job(
            func=scheduled_task_binance_by_websocket,
            trigger='date',
            next_run_time=datetime.now()
        )
    else:
        scheduler.add_job(
            func=scheduled_task_binance,
            trigger='interval',
            seconds=settings.binance_scheduler.interval,
            start_date=datetime.now()
        )

    account_storage = PostgresAccountStorage(settings.postgres)
    asyncio.run(account_storage.cache_all_active_accounts('coingeko'))
    scheduler.add_job(
        scheduled_task_coingeko,
        trigger='interval',
        seconds=settings.coingeko_scheduler.interval,
        start_date=datetime.now()
    )

    try:
        logger.debug('Starting scheduler...')
        scheduler.start()
        logger.debug('Scheduler started')
    except KeyboardInterrupt:  # For local run
        signal.raise_signal(signal.SIGTERM)
