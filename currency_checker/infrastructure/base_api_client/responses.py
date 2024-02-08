from typing import Type, TypeVar

from pydantic import BaseModel, parse_raw_as

from currency_checker.infrastructure.base_api_client.exceptions import (
    ApiClientInvalidResponseError,
    ApiClientResponseError,
)
from currency_checker.infrastructure.base_api_client.requests import RequestInfo


T = TypeVar('T')


class Response(BaseModel):
    request_info: RequestInfo
    status: int
    data: str
    content_type: str

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise ApiClientResponseError(
                self.request_info,
                status=self.status,
                message=self.data,
            )

    def parse(self, model: Type[T]) -> T:
        try:
            return parse_raw_as(model, self.data, content_type=self.content_type)
        except (ValueError, TypeError) as exc:
            raise ApiClientInvalidResponseError(exc)
