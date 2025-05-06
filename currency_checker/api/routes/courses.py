from fastapi import APIRouter, Query, Request

from currency_checker.api.models import Course, CoursesResponse
from currency_checker.domain.models import Direction, Exchanger
from currency_checker.domain.services import BinanceService, CoingekoService


router = APIRouter(prefix='/courses', tags=['Currency courses'])


@router.get(
    '',
    response_model=CoursesResponse,
)
async def courses_handler(
    request: Request,
    exchanger: Exchanger = Query(default=Exchanger.BINANCE),
    directions: list[Direction] | None = Query(
        default=None,
        example=[Direction.BTC_RUB, Direction.BTC_USD],
    ),
) -> CoursesResponse:
    if not directions:
        directions = [direction for direction in Direction]

    service: BinanceService | CoingekoService
    match exchanger:
        case Exchanger.BINANCE:
            service = request.app.state.binance
        case _:
            service = request.app.state.coingeko

    result = {
        direction: await service.get_course_value(direction)
        for direction in directions
    }

    return CoursesResponse(
        exchanger=exchanger,
        courses=[
            Course(
                direction=direction,
                value=result[direction]
            ) for direction in directions
        ]
    )
