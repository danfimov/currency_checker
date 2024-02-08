from typing import Any, Optional, Union

from currency_checker.infrastructure.base_api_client.requests import RequestInfo


class ApiClientError(Exception):
    def __init__(self, data: Any = None, *args: Any):
        super().__init__(data, *args)
        self.error: Optional[str] = None
        self.status: Optional[Union[int, str]] = None
        self.detailed_error: Optional[str] = None
        self.raw = data


class ApiClientResponseError(ApiClientError):
    def __init__(
        self,
        request_info: RequestInfo,
        *,
        status: int,
        message: str = "",
    ) -> None:
        self.request_info = request_info
        self.status = status
        self.message = message

    def __str__(self) -> str:
        return "{}, message={!r}, url={!r}".format(
            self.status,
            self.message,
            self.request_info.url,
        )

    def __repr__(self) -> str:
        args = f'{self.request_info!r}, status={self.status!r}'
        if self.message != '':
            args += f', message={self.message!r}'
        return f'{type(self).__name__}({args})'


class ApiClientUnavailableError(ApiClientError):
    pass


class ApiClientAuthError(ApiClientError):
    pass


class ApiClientInvalidResponseError(ApiClientError):
    pass
