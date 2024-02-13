import json
from logging import getLogger
from typing import AsyncGenerator

from aiohttp import ClientSession, WSMsgType
from starlette import status

from currency_checker.domain.exchange_clients.base import AbstractExchangeClient
from currency_checker.domain.models import CurrencyRateBinance, DirectionBinance
from currency_checker.infrastructure.base_api_client.base_client import BaseClient, BaseSession
from currency_checker.infrastructure.base_api_client.exceptions import ApiClientResponseError


logger = getLogger(__name__)


class BinanceClient(AbstractExchangeClient, BaseClient):
    session_class = BaseSession
    _api_service_name: str = 'binance'

    def __init__(self) -> None:
        super().__init__(
            base_uri='https://api.binance.com/api/v3/',
            enable_metrics=True,
            client_name='currency_checker',
        )
        self.session = self.get_session()

    async def get_price(
        self,
        directions: list[DirectionBinance]
    ) -> list[CurrencyRateBinance]:
        directions_str = '","'.join(directions) if len(directions) > 1 else f'"{directions[0]}"'
        response = await self.session.request(
            method='get',
            path_template='ticker/price',
            params={
                'symbols': f'["{directions_str}"]'
            },
        )

        if response.status != status.HTTP_200_OK:
            raise ApiClientResponseError(
                request_info=response.request_info,
                status=response.status,
                message=response.data,
            )
        raw_response = json.loads(response.data)
        return [
            CurrencyRateBinance(
                symbol=item['symbol'],
                price=item['price'],
            ) for item in raw_response
        ]


class BinanceWebsocketClient(AbstractExchangeClient):
    def __init__(self, base_url: str = 'wss://stream.binance.com:9443') -> None:
        self.base_uri = base_url

    @staticmethod
    def _parse_price(raw_price_response: str) -> CurrencyRateBinance:
        price_response = json.loads(raw_price_response)
        return CurrencyRateBinance(
            symbol=price_response['data']['s'],
            price=float(price_response['data']['w'])
        )

    async def get_price(  # type: ignore
        self, directions: list[DirectionBinance]
    ) -> AsyncGenerator[CurrencyRateBinance, None]:
        async with ClientSession(base_url=self.base_uri) as session:
            async with session.ws_connect('/stream') as websocket_connection:
                subscribe_message = {
                    "method": "SUBSCRIBE",
                    "params": [
                        f"{direction.lower()}@avgPrice" for direction in directions
                    ],
                    "id": None,
                }
                await websocket_connection.send_json(subscribe_message)

                first_message = True

                async for msg in websocket_connection:
                    if first_message:  # skip first message about successful subscription
                        first_message = False
                        continue

                    match msg.type:
                        case WSMsgType.TEXT:
                            yield self._parse_price(msg.data)
                        case WSMsgType.CLOSED:
                            logger.info('Websocket connection closed')
                            break
                        case WSMsgType.ERROR:
                            logger.error('Received websocket connection error: %s', msg.data)
                            break
