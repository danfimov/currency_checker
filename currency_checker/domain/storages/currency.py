from abc import ABC, abstractmethod

from redis.asyncio import Redis

from currency_checker.infrastructure.settings import RedisSettings


class AbstractCurrencyStorage(ABC):
    @abstractmethod
    async def get_key(self, key: str) -> float:
        ...

    @abstractmethod
    async def set_key(self, key: str, value: float) -> None:
        ...


class RedisCurrencyStorage(AbstractCurrencyStorage):
    def __init__(self, redis_settings: RedisSettings, key_prefix: str = '') -> None:
        self.redis = Redis(
            host=redis_settings.host,
            port=redis_settings.port,
            db=redis_settings.database,
        )
        self.key_prefix = key_prefix

    async def get_key(self, key: str) -> float:
        return float(await self.redis.get(f'{self.key_prefix}/{key}'))

    async def set_key(self, key: str, value: float) -> None:
        await self.redis.set(f'{self.key_prefix}/{key}', value)
