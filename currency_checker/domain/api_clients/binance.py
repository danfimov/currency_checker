import json

from currency_checker.domain.api_clients.base import AbstractCurrencyClient
from currency_checker.infrastructure.base_api_client.base_client import BaseSession
from currency_checker.infrastructure.base_api_client.exceptions import ApiClientResponseError


class BinanceApiClient(AbstractCurrencyClient):
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
        currency_pairs: list[str]
    ) -> dict[str, dict[str, float]]:
        currency_pairs_str = '","'.join(currency_pairs) if len(currency_pairs) > 1 else f'"{currency_pairs[0]}"'
        response = await self.session.request(
            method='get',
            path_template='ticker/price',
            params={
                'symbols': f'["{currency_pairs_str}"]'
            },
        )

        if response.status != 200:
            raise ApiClientResponseError(
                request_info=response.request_info,
                status=response.status,
                message=response.data,
            )
        return json.loads(response.data)
