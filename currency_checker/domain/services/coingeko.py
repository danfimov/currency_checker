from .base import AbstractCurrencyService
from currency_checker.domain.models import CurrenciesCoinbase, Direction
from currency_checker.domain.storages.currency import AbstractCurrencyStorage


class CoingekoService(AbstractCurrencyService):
    def __init__(self, storage: AbstractCurrencyStorage) -> None:
        self.storage = storage

    async def get_course_value(self, direction: Direction) -> float:
        mapping = {  # if there will be more currencies this mapping might be stored in database
            Direction.USDTTRC_USD: 'TRXUSD',
            Direction.USDTTRC_RUB: 'TRXRUB',
            Direction.USDTERC_USD: 'USDTUSD',
            Direction.USDTERC_RUB: 'USDTRUB',
            Direction.ETH_RUB: 'ETHRUB',
            Direction.ETH_USD: 'ETHUSD',
            Direction.BTC_RUB: 'BTCRUB',
            Direction.BTC_USD: 'BTCUSD',
        }
        return await self.storage.get_key(mapping[direction])

    async def save_course_values(self, course_values: dict) -> None:
        mapping = {  # if there will be more currencies this mapping might be stored in database
            CurrenciesCoinbase.TRON: 'TRX',
            CurrenciesCoinbase.RUB: 'RUB',
            CurrenciesCoinbase.USD: 'USD',
            CurrenciesCoinbase.TETHER: 'USDT',
            CurrenciesCoinbase.ETHEREUM: 'ETH',
            CurrenciesCoinbase.BITCOIN: 'BTC',
        }
        for first_currency, vs_currencies in course_values.items():
            for second_currency, rate in vs_currencies.items():
                await self.storage.set_key(
                    f'{mapping[first_currency]}{mapping[second_currency]}',
                    rate
                )
