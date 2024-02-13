from currency_checker.domain.models import CurrencyRateBinance, Direction, DirectionBinance
from currency_checker.domain.services import AbstractCurrencyService
from currency_checker.domain.storages.currency import AbstractCurrencyStorage


class BinanceService(AbstractCurrencyService):
    def __init__(self, storage: AbstractCurrencyStorage) -> None:
        self.storage = storage

    async def get_course_value(self, direction: Direction) -> float:
        if direction == Direction.USDTERC_USD:
            # let's assume that USDT and USD is the same currency (because rate ~1)
            return 1
        if direction == Direction.USDTTRC_RUB:
            # on this platform there are no info about TRX-RUB pair
            trx_to_usd = await self.storage.get_key(DirectionBinance.TRX_USDT)
            usd_to_rub = await self.storage.get_key(DirectionBinance.USDT_RUB)
            return trx_to_usd * usd_to_rub
        mapping = {  # if there will be more currencies this mapping might be stored in database
            Direction.USDTTRC_USD: DirectionBinance.TRX_USDT,
            Direction.USDTERC_RUB: DirectionBinance.USDT_RUB,
            Direction.ETH_RUB: DirectionBinance.ETH_RUB,
            Direction.ETH_USD: DirectionBinance.ETH_USDT,
            Direction.BTC_RUB: DirectionBinance.BTC_RUB,
            Direction.BTC_USD: DirectionBinance.BTC_USDT,
        }
        return await self.storage.get_key(mapping[direction])

    async def save_course_values(self, currency_rate: CurrencyRateBinance) -> None:
        await self.storage.set_key(currency_rate.symbol, currency_rate.price)
