import signal
from logging import getLogger
from pathlib import Path
from sys import exit
from types import FrameType

from dramatiq import Worker

from currency_checker.infrastructure.logging import configure_logging
from currency_checker.infrastructure.settings import Settings
from currency_checker.scheduler.jobs import redis_broker


logger = getLogger(__name__)
workers: Worker | None = None


def sigterm_handler(_signal: int, _frame: FrameType | None) -> None:
    logger.debug('SIGTERM received, stopping workers...')
    if workers is not None:
        workers.stop()
    logger.debug('Workers stopped')
    exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)


if __name__ == '__main__':
    settings = Settings()
    configure_logging(
        path_to_log_config=Path.cwd() / settings.log.config_path,
        root_level=settings.log.level,
    )
    logger.debug('Starting workers...')
    workers = Worker(redis_broker, worker_threads=8)
    workers.start()
    logger.debug('Workers started')

    while True:
        try:
            signal.pause()  # Keep the main thread running
        except KeyboardInterrupt:  # For local run
            signal.raise_signal(signal.SIGTERM)
