from abc import ABC, abstractmethod
from logging import getLogger

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.asyncio import AsyncIO

from currency_checker.domain.api_clients import AbstractCurrencyClient, BinanceApiClient, CoingekoApiClient
from currency_checker.domain.services import AbstractCurrencyService, BinanceService, CoingekoService
from currency_checker.domain.storages.currency import RedisCurrencyStorage
from currency_checker.infrastructure.settings import Settings


logger = getLogger(__name__)
settings = Settings()

# Set broker for scheduler process
# Without it scheduler will start to work with AMQP instead of REdis
redis_broker = RedisBroker(
    host=settings.redis.host,
    port=settings.redis.port,
    db=settings.redis.database,
    middleware=[AsyncIO()],
)
dramatiq.set_broker(redis_broker)


class Job(ABC):
    def __init__(self, client: AbstractCurrencyClient, service: AbstractCurrencyService):
        self.client = client
        self.service = service

    @abstractmethod
    async def execute(self) -> None:
        ...


class CoingekoJob(Job):
    async def execute(self) -> None:
        currency_rates = await self.client.get_price(
            currencies=['bitcoin', 'ethereum', 'tether', 'tron'],
            vs_currencies=['usd', 'rub'],
        )
        await self.service.save_currency_rates(currency_rates)


class BinanceJob(Job):
    async def execute(self) -> None:
        currency_rates = await self.client.get_price(
            currency_pairs=["BTCUSDT", "BTCRUB", "TRXUSDT", "USDTRUB", "ETHRUB", "ETHUSDT"],
        )
        await self.service.save_currency_rates(currency_rates)


@dramatiq.actor
async def binance_get_currency_rates() -> None:
    job = BinanceJob(
        service=BinanceService(
            RedisCurrencyStorage(settings.redis, 'binance')
        ),
        client=BinanceApiClient()
    )
    logger.info('Job get_currency_rates started')
    await job.execute()
    await job.client.close()
    logger.info('Job get_currency_rates ended')


@dramatiq.actor
async def coingeko_get_currency_rates(api_token: str) -> None:
    job = CoingekoJob(
        service=CoingekoService(
            RedisCurrencyStorage(settings.redis, 'coingeko')
        ),
        client=CoingekoApiClient(api_token)
    )
    logger.info('Job get_currency_rates started')
    await job.execute()
    await job.client.close()
    logger.info('Job get_currency_rates ended')
