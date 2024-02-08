from abc import ABC, abstractmethod

from currency_checker.infrastructure.base_api_client.base_client import BaseClient


class AbstractCurrencyClient(BaseClient, ABC):
    @abstractmethod
    async def get_price(self, *args, **kwargs) -> dict:  # type: ignore
        ...
