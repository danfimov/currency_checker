from abc import ABC, abstractmethod
from typing import Any

from currency_checker.domain.models import Direction


class AbstractCurrencyService(ABC):
    @abstractmethod
    async def get_course_value(self, direction: Direction) -> float:
        ...

    @abstractmethod
    async def save_course_values(self, course_values: Any) -> None:
        ...
