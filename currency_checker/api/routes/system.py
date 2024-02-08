import socket

from fastapi import APIRouter, Request

from currency_checker import APP_NAME


router = APIRouter(tags=['System'])


@router.get('/ping')
async def health_check_handler(request: Request) -> dict:
    return {
        'service': APP_NAME,
        'version': request.app.version,
        'hostname': socket.gethostname(),
    }
