from typing import Literal

from fastapi import APIRouter, Query, Request

from currency_checker.domain.services import BinanceService, CoingekoService


router = APIRouter(prefix='/courses', tags=['Currency courses'])


@router.get('/')
async def courses_handler(
    request: Request,
    exchanger: Literal['binance', 'coingeko'] = Query(default='binance'),
    directions: list[
        Literal[
            'BTC-RUB',
            'BTC-USD',
            'ETH-RUB',
            'ETH-USD',
            'USDTTRC-RUB',
            'USDTTRC-USD',
            'USDTERC-RUB',
            'USDTERC-USD',
        ]
    ] = Query(default_factory=list),
) -> dict:
    if not directions:
        directions = [
            'BTC-RUB', 'BTC-USD', 'ETH-RUB', 'ETH-USD',
            'USDTTRC-RUB', 'USDTTRC-USD', 'USDTERC-RUB', 'USDTERC-USD'
    ]

    service: BinanceService | CoingekoService
    if exchanger == 'binance':
        service = request.app.state.binance
    else:
        service  = request.app.state.coingeko

    result = {}
    for direction in directions:
        result[direction] = await service.get_currency_rate(direction)

    return {
        "exchanger": exchanger,
        "courses": [
            {
                "direction": direction,
                "value": result[direction]
            } for direction in directions
        ]
    }
