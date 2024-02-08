from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter()


@router.get('/', include_in_schema=False)
async def docs_redirect_handler() -> RedirectResponse:
    return RedirectResponse(url='/docs')
