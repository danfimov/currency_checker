from currency_checker.domain.services import AbstractCurrencyService
from currency_checker.domain.storages.currency import AbstractCurrencyStorage


class BinanceService(AbstractCurrencyService):
    def __init__(self, storage: AbstractCurrencyStorage) -> None:
        self.storage = storage

    async def get_currency_rate(self, currency: str) -> float:
        if currency == 'USDTERC-USD':
            # let's assume that USDT and USD is the same currency (because rate ~1)
            return 1
        if currency == 'USDTTRC-RUB':
            # on this platform there are no info about TRX-RUB pair
            trx_to_usd = await self.storage.get_key('TRXUSDT')
            usd_to_rub = await self.storage.get_key('USDTRUB')
            return trx_to_usd * usd_to_rub
        mapping = {  # if there will be more currencies this mapping might be stored in database
            'USDTTRC-USD': 'TRXUSDT',
            'USDTERC-RUB': 'USDTRUB',
            'ETH-RUB': 'ETHRUB',
            'ETH-USD': 'ETHUSDT',
            'BTC-RUB': 'BTCRUB',
            'BTC-USD': 'BTCUSDT'
        }
        return await self.storage.get_key(mapping[currency])

    async def save_currency_rates(self, currency_rates: dict) -> None:
        for item in currency_rates:
            await self.storage.set_key(item['symbol'], item['price'])
