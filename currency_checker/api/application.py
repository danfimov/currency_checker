from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from pydantic import BaseModel

from currency_checker import APP_NAME, __version__
from currency_checker.api.routes.courses import router as courses_router
from currency_checker.api.routes.docs import router as docs_router
from currency_checker.api.routes.system import router as system_router
from currency_checker.domain.services.binance import BinanceService
from currency_checker.domain.services.coingeko import CoingekoService
from currency_checker.domain.storages.currency import RedisCurrencyStorage
from currency_checker.infrastructure.logging import configure_logging
from currency_checker.infrastructure.settings import Settings


class AppState(BaseModel):
    settings: Settings
    coingeko: CoingekoService
    binance: BinanceService

    class Config:
        arbitrary_types_allowed = True


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator:
    settings = Settings()

    application.state = AppState(
        settings=settings,
        coingeko=CoingekoService(RedisCurrencyStorage(redis_settings=settings.redis, key_prefix='coingeko')),
        binance=BinanceService(RedisCurrencyStorage(redis_settings=settings.redis, key_prefix='binance')),
    )  # type: ignore

    yield

    ...


def get_app() -> FastAPI:
    settings = Settings()
    configure_logging(
        path_to_log_config=Path.cwd().parent.parent.parent / settings.log.config_path,
        root_level=settings.log.level,
    )
    app = FastAPI(
        title=APP_NAME,
        version=__version__,
        lifespan=lifespan,
    )

    app.include_router(system_router)
    app.include_router(docs_router)
    app.include_router(courses_router, prefix='/v1')

    return app
