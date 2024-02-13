from enum import StrEnum

from pydantic import BaseModel


class Account(BaseModel):
    token: str

    class Config:
        orm_mode = True


class Exchanger(StrEnum):
    BINANCE = "binance"
    COINBASE = "coinbase"


class Direction(StrEnum):
    BTC_RUB = 'BTC-RUB'
    BTC_USD = 'BTC-USD'
    ETH_RUB = 'ETH-RUB'
    ETH_USD = 'ETH-USD'
    USDTTRC_RUB = 'USDTTRC-RUB'
    USDTTRC_USD = 'USDTTRC-USD'
    USDTERC_RUB = 'USDTERC-RUB'
    USDTERC_USD = 'USDTERC-USD'


class CurrenciesCoinbase(StrEnum):
    TRON = 'tron'
    RUB = 'rub'
    USD = 'usd'
    TETHER = 'tether'
    ETHEREUM = 'ethereum'
    BITCOIN = 'bitcoin'


class DirectionBinance(StrEnum):
    BTC_RUB = 'BTCRUB'
    BTC_USDT = 'BTCUSDT'
    ETH_RUB = 'ETHRUB'
    ETH_USDT = 'ETHUSD'
    TRX_USDT = 'TRXUSDT'
    USDT_RUB = 'USDTRUB'


class CurrencyRateBinance(BaseModel):
    symbol: DirectionBinance
    price: float
