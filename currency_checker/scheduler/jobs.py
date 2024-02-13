from abc import ABC, abstractmethod
from logging import getLogger

import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware.asyncio import AsyncIO

from currency_checker.domain.exchange_clients import (
    AbstractExchangeClient,
    BinanceClient,
    BinanceWebsocketClient,
    CoingekoClient,
)
from currency_checker.domain.models import CurrenciesCoinbase, DirectionBinance
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
    def __init__(self, client: AbstractExchangeClient, service: AbstractCurrencyService):
        self.client = client
        self.service = service

    @abstractmethod
    async def execute(self) -> None:
        ...


class CoingekoJob(Job):
    async def execute(self) -> None:
        course_values = await self.client.get_price(
            currencies=[
                CurrenciesCoinbase.BITCOIN,
                CurrenciesCoinbase.ETHEREUM,
                CurrenciesCoinbase.TETHER,
                CurrenciesCoinbase.TRON
            ],
            vs_currencies=[
                CurrenciesCoinbase.USD,
                CurrenciesCoinbase.RUB
            ],
        )
        await self.service.save_course_values(course_values)


class BinanceJob(Job):
    async def execute(self) -> None:
        currency_rates = await self.client.get_price(
            directions=[
                DirectionBinance.BTC_USDT,
                DirectionBinance.BTC_RUB,
                DirectionBinance.TRX_USDT,
                DirectionBinance.USDT_RUB,
                DirectionBinance.ETH_RUB,
                DirectionBinance.ETH_USDT,
            ],
        )
        for currency_rate in currency_rates:
            await self.service.save_course_values(currency_rate)


class BinanceWebsocketJob(Job):
    async def execute(self) -> None:
        async for currency_rate in self.client.get_price(
            directions=[
                DirectionBinance.BTC_USDT,
                DirectionBinance.BTC_RUB,
                DirectionBinance.TRX_USDT,
                DirectionBinance.USDT_RUB,
                DirectionBinance.ETH_RUB,
                DirectionBinance.ETH_USDT,
            ],
        ):
            await self.service.save_course_values(currency_rate)


@dramatiq.actor
async def binance_get_currency_rates() -> None:
    job = BinanceJob(
        service=BinanceService(
            RedisCurrencyStorage(settings.redis, 'binance')
        ),
        client=BinanceClient()
    )
    logger.info('Job get_currency_rates started')
    await job.execute()
    await job.client.close()
    logger.info('Job get_currency_rates ended')


@dramatiq.actor
async def binance_get_currency_rates_by_websocket() -> None:
    job = BinanceWebsocketJob(
        service=BinanceService(
            RedisCurrencyStorage(settings.redis, 'binance')
        ),
        client=BinanceWebsocketClient(),
    )
    logger.info('Job get_currency_rates started')
    await job.execute()
    logger.info('Job get_currency_rates ended')
    binance_get_currency_rates_by_websocket.send()  # trigger same task after one will end with connection error etc.


@dramatiq.actor
async def coingeko_get_currency_rates(api_token: str) -> None:
    job = CoingekoJob(
        service=CoingekoService(
            RedisCurrencyStorage(settings.redis, 'coingeko')
        ),
        client=CoingekoClient(api_token)
    )
    logger.info('Job get_currency_rates started')
    await job.execute()
    await job.client.close()
    logger.info('Job get_currency_rates ended')
