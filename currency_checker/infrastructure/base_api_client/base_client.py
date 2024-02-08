import asyncio
import logging
import time
from collections.abc import Awaitable, Callable, Mapping
from decimal import Decimal
from json import JSONEncoder
from types import SimpleNamespace
from typing import Any, Generic, Optional, Type, TypeVar, Union

import aiohttp
from aiohttp import ClientError, ClientSession, DummyCookieJar, TCPConnector, TraceConfig, hdrs, tracing
from prometheus_client import Summary
from pydantic import BaseModel
from pydantic.json import pydantic_encoder
from yarl import URL

from currency_checker.infrastructure.base_api_client.base_throttler import BaseThrottler, DoNothingThrottler
from currency_checker.infrastructure.base_api_client.exceptions import ApiClientError
from currency_checker.infrastructure.base_api_client.metrics import HTTP_REQUEST_DURATION_SECONDS
from currency_checker.infrastructure.base_api_client.requests import RequestInfo
from currency_checker.infrastructure.base_api_client.responses import Response


class BaseSession:
    _path_prefix: str = ''

    def __init__(
        self,
        *args: Any,
        http_session: aiohttp.ClientSession,
        base_uri: Union[str, URL],
        proxy: Optional[URL] = None,
        throttler: Optional[BaseThrottler] = None,
        retry_num: int = 0,
        retry_interval: int = 0,
        enable_metrics: bool = False,
        api_service_name: str = '',
        client_name: str = '',
        http_request_duration_metric: Summary = HTTP_REQUEST_DURATION_SECONDS,
        **kwargs: Any,
    ) -> None:
        self._http_session = http_session
        self._base_uri = URL(base_uri) / self._path_prefix
        self._throttler = throttler or DoNothingThrottler()
        self._retry_num = retry_num
        self._retry_interval = retry_interval
        self._enable_metrics = enable_metrics
        self._api_service_name = api_service_name
        self._client_name = client_name

        self._http_request_duration_metric = http_request_duration_metric
        self._session_args = args
        self._session_kwargs = kwargs
        self._request_kwargs: dict[str, Any] = {'proxy': proxy, 'allow_redirects': False}

        self._logger = logging.getLogger(
            f'{self.__module__}.{type(self).__name__}'
        )

    async def request(
        self,
        method: str,
        path_template: str,
        *,
        path_params: Optional[dict] = None,
        params: Optional[dict[str, Union[str, int, float]]] = None,
        headers: Optional[dict[str, str]] = None,
        accept: Optional[str] = 'application/json',
        data: Any = None,
        json: Any = None,
    ) -> Response:
        """
        :param path_template: template of URL path, used with `path_params`
        :param path_params: parameters for `path_template`
        """
        path_params = path_params or {}
        path = path_template.format(**path_params)
        url = self._base_uri / path
        headers = headers or {}

        if accept is not None:
            if hdrs.ACCEPT in headers:
                raise ValueError("headers already have 'Accept' header")
            headers[hdrs.ACCEPT] = accept

        async with self._throttler:
            metric_response_status: str = ''
            started_at = time.monotonic()
            try:
                async with self._http_session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    data=data,
                    json=json,
                    **self._request_kwargs,
                ) as response:
                    # TODO Возможно, надо переделать на response.read().
                    #  Сейчас упадем, если бинарь, или, не UTF-8 и не указана кодировка.
                    #  Обсуждение: https://gitlab.cm.expert/python/cme-api-clients/-/merge_requests/226#note_304587
                    body = await response.text()
            except ClientError as e:
                raise ApiClientError(str(e))
            else:
                metric_response_status = str(response.status)
            finally:
                if self._enable_metrics and path_template is not None:
                    self._http_request_duration_metric.labels(
                        api_service_name=self._api_service_name,
                        client_name=self._client_name,
                        base_uri=str(self._base_uri),
                        path=path_template,
                        method=method,
                        response_status=metric_response_status,
                    ).observe(time.monotonic() - started_at)

        r = Response(
            request_info=RequestInfo(
                method=method, url=url
            ),
            status=response.status,
            data=body,
            content_type=response.content_type,
        )
        return r

    async def retry(
        self,
        cor_func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any
    ) -> Any:
        for attempt in range(self._retry_num + 1):
            try:
                return await cor_func(*args, **kwargs)
            except Exception as e:
                self._logger.info(
                    'Attempt: %s. Error: %s ', attempt + 1, e
                )
                if attempt == self._retry_num:
                    raise
                await asyncio.sleep(self._retry_interval)

    async def request_with_retry(
        self,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        return await self.retry(
            self.request, *args, **kwargs
        )


_SessionClassT = TypeVar('_SessionClassT', bound=BaseSession)


class BaseClient(Generic[_SessionClassT]):
    session_class: Type[_SessionClassT]
    # Name of the service the API belongs, e.g: int-api
    _api_service_name: str = ''

    def __init__(
        self,
        base_uri: Union[str, URL],
        mock_base_uri: Optional[Union[str, URL]] = None,
        throttler: Optional[BaseThrottler] = None,
        retry_num: int = 0,
        retry_interval: int = 0,
        headers: Optional[Mapping[str, str]] = None,
        branch: Optional[str] = None,
        proxy: Optional[Union[str, URL]] = None,
        connection_limit: int = 100,
        enable_metrics: bool = False,
        client_name: str = '',
    ) -> None:
        """
        :param client_name: Name of the client who use API
        """
        self._base_uri = URL(base_uri)
        self._mock_base_uri = URL(mock_base_uri) if mock_base_uri else None
        self._throttler = throttler
        self._retry_num = retry_num
        self._retry_interval = retry_interval
        self._proxy = URL(proxy) if proxy else None
        self._enable_metrics = enable_metrics
        if self._enable_metrics and not (self._api_service_name and client_name):
            raise ValueError(
                '`api_service_name` and `client_name` must be specified '
                'when `enable_metrics` is True'
            )
        self._client_name = client_name

        self._logger = logging.getLogger(
            f'{self.__module__}.{type(self).__name__}'
        )

        trace_config: Optional[TraceConfig] = None
        if self._logger.level <= logging.INFO:
            trace_config = TraceConfig()
            trace_config.on_request_start.append(self._on_request_start)
            trace_config.on_request_chunk_sent.append(self._on_request_chunk_sent)
            trace_config.on_request_end.append(self._on_request_end)

        http_session_headers: dict[str, str] = {}
        if branch:
            http_session_headers['x-branch-name'] = branch
        if headers:
            http_session_headers.update(headers)

        self._http_session = aiohttp.ClientSession(
            cookie_jar=DummyCookieJar(),
            json_serialize=JSONEncoder(default=self._json_encoder).encode,
            trace_configs=[trace_config] if trace_config else None,
            headers=http_session_headers,
            connector=TCPConnector(limit=connection_limit)
        )
        self._sessions: dict[tuple[Any, ...], _SessionClassT] = {}

    def get_session(self, *args: Any, mock: bool = False, **kwargs: Any) -> _SessionClassT:
        """Sum of positional args and mock is a session key."""
        session_key = (*args, mock)
        base_uri = self._base_uri if not mock else self._mock_base_uri or self._base_uri
        if session_key not in self._sessions:
            session = self.session_class(
                *args,
                http_session=self._http_session,
                base_uri=base_uri,
                throttler=self._throttler,
                retry_num=self._retry_num,
                retry_interval=self._retry_interval,
                proxy=self._proxy,
                enable_metrics=self._enable_metrics,
                api_service_name=self._api_service_name,
                client_name=self._client_name,
                **kwargs,
            )
            self._sessions[session_key] = session

        return self._sessions[session_key]

    async def close(self) -> None:
        await self._http_session.close()

    @classmethod
    def _json_encoder(cls, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return obj.dict(by_alias=True)
        elif isinstance(obj, Decimal):
            return str(obj)
        else:
            return pydantic_encoder(obj)

    @staticmethod
    async def _on_request_start(
        session: ClientSession, context: SimpleNamespace, params: tracing.TraceRequestStartParams
    ) -> None:
        context.request_body = ''

    @staticmethod
    async def _on_request_chunk_sent(
        session: ClientSession, context: SimpleNamespace, params: tracing.TraceRequestChunkSentParams
    ) -> None:
        context.request_body += params.chunk.decode('utf-8', 'replace')

    async def _on_request_end(
        self,
        session: ClientSession,
        context: SimpleNamespace,
        params: tracing.TraceRequestEndParams
    ) -> None:
        self._logger.info(
            "Request: %s %s",
            params.method,
            params.url
        )
