from abc import ABC, abstractmethod


class AbstractExchangeClient(ABC):
    @abstractmethod
    async def get_price(self, *args, **kwargs):  # type: ignore
        ...

    async def close(self) -> None:
        ...
