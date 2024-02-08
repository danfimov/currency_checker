import abc
from types import TracebackType
from typing import Optional, Type


class BaseThrottler(abc.ABC):
    @abc.abstractmethod
    async def acquire(self) -> None:
        ...

    async def __aenter__(self) -> None:
        await self.acquire()

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType]
    ) -> Optional[bool]:
        pass


class DoNothingThrottler(BaseThrottler):
    """
    Do nothing throttler
    """
    async def acquire(self) -> None:
        pass
