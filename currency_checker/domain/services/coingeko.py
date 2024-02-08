from .base import AbstractCurrencyService
from currency_checker.domain.storages.currency import AbstractCurrencyStorage


class CoingekoService(AbstractCurrencyService):
    def __init__(self, storage: AbstractCurrencyStorage) -> None:
        self.storage = storage

    async def get_currency_rate(self, currency: str) -> float:
        mapping = {  # if there will be more currencies this mapping might be stored in database
            'USDTTRC-USD': 'TRXUSD',
            'USDTTRC-RUB': 'TRXRUB',
            'USDTERC-USD': 'USDTUSD',
            'USDTERC-RUB': 'USDTRUB',
            'ETH-RUB': 'ETHRUB',
            'ETH-USD': 'ETHUSD',
            'BTC-RUB': 'BTCRUB',
            'BTC-USD': 'BTCUSD'
        }
        return await self.storage.get_key(mapping[currency])

    async def save_currency_rates(self, currency_rates: dict) -> None:
        mapping = {  # if there will be more currencies this mapping might be stored in database
            'tron': 'TRX',
            'rub': 'RUB',
            'usd': 'USD',
            'tether': 'USDT',
            'ethereum': 'ETH',
            'bitcoin': 'BTC',
        }
        for first_currency, vs_currencies in currency_rates.items():
            for second_currency, rate in vs_currencies.items():
                await self.storage.set_key(
                    f'{mapping[first_currency]}{mapping[second_currency]}',
                    rate
                )
