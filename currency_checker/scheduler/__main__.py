import signal
from datetime import datetime
from logging import getLogger
from types import FrameType

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.blocking import BlockingScheduler

from currency_checker.infrastructure.logging import configure_logging
from currency_checker.infrastructure.settings import Settings
from currency_checker.scheduler.jobs import binance_get_currency_rates, coingeko_get_currency_rates


logger = getLogger(__name__)
scheduler: BlockingScheduler | None = None


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
    coingeko_get_currency_rates.send()


if __name__ == "__main__":
    settings = Settings()
    configure_logging(
        path_to_log_config=settings.log.config_path,
        root_level=settings.log.level,
    )

    job_stores = {
        'default': RedisJobStore(
            db=settings.redis.database,
            host=settings.redis.host,
            port=settings.redis.port,
        )
    }
    scheduler = BlockingScheduler(jobstores=job_stores)
    # scheduler.add_job(
    #     func=scheduled_task_binance,
    #     trigger='interval',
    #     seconds=settings.binance_scheduler.interval,
    #     start_date=datetime.now()
    # )
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
