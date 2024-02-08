from abc import ABC, abstractmethod


class AbstractCurrencyService(ABC):
    @abstractmethod
    async def get_currency_rate(self, currency: str) -> float:
        ...

    @abstractmethod
    async def save_currency_rates(self, currency_rates: dict) -> None:
        ...
