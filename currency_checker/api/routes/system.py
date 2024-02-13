import socket

from fastapi import APIRouter, Request

from currency_checker import APP_NAME
from currency_checker.api.models import PingResponse


router = APIRouter(tags=['System'])


@router.get(
    '/ping',
    response_model=PingResponse,
)
async def health_check_handler(request: Request) -> PingResponse:
    return PingResponse(
        service=APP_NAME,
        version=request.app.version,
        hostname=socket.gethostname(),
    )
