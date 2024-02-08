import json

from currency_checker.domain.api_clients.base import AbstractCurrencyClient
from currency_checker.infrastructure.base_api_client.base_client import BaseSession
from currency_checker.infrastructure.base_api_client.exceptions import ApiClientResponseError


class CoingekoApiClient(AbstractCurrencyClient):
    session_class = BaseSession
    _api_service_name: str = 'coin_geko'

    def __init__(self, api_key: str) -> None:
        super().__init__(
            base_uri='https://api.coingecko.com/api/v3/simple/',
            enable_metrics=True,
            client_name='currency_checker',

        )
        self.api_key = api_key
        self.session = self.get_session()

    async def get_price(
        self,
        currencies: list[str],
        vs_currencies: list[str],
    ) -> dict[str, dict[str, float]]:
        response = await self.session.request(
            method='get',
            path_template='price',
            params={
                'ids': ','.join(currencies),
                'vs_currencies': ','.join(vs_currencies),
                'x_cg_demo_api_key': self.api_key,
            }
        )

        if response.status != 200:
            raise ApiClientResponseError(
                request_info=response.request_info,
                status=response.status,
                message=response.data,
            )
        return json.loads(response.data)
