from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_async.aio.web import MetricsHTTPServer
from pydantic import BaseModel

from currency_checker import APP_NAME, __version__
from currency_checker.api.routes.courses import router as courses_router
from currency_checker.api.routes.docs import router as docs_router
from currency_checker.api.routes.system import router as system_router
from currency_checker.domain.services.binance import BinanceService
from currency_checker.domain.services.coingeko import CoingekoService
from currency_checker.domain.storages.currency import RedisCurrencyStorage
from currency_checker.infrastructure.logging import configure_logging
from currency_checker.infrastructure.metrics import start_metric_server
from currency_checker.infrastructure.settings import Settings


class AppState(BaseModel):
    settings: Settings
    coingeko: CoingekoService
    binance: BinanceService
    metric_server: MetricsHTTPServer | None = None

    class Config:
        arbitrary_types_allowed = True


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator:
    settings = Settings()

    metric_server = None
    if settings.api_metrics_port:
        metric_server = await start_metric_server(
            port=settings.api_metrics_port
        )

    app_state = AppState(
        settings=settings,
        coingeko=CoingekoService(RedisCurrencyStorage(settings=settings.redis, key_prefix='coingeko')),
        binance=BinanceService(RedisCurrencyStorage(settings=settings.redis, key_prefix='binance')),
        metric_server=metric_server,
    )

    application.state = app_state  # type: ignore

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

    if settings.api_metrics_port:  # only if metrics server enabled
        from starlette_exporter import PrometheusMiddleware

        app.add_middleware(
            PrometheusMiddleware,
            app_name=APP_NAME,
            prefix='http_server',
            group_paths=True,
            skip_paths=['/ping', '/docs', '/redoc', '/openapi.json', '/'],
        )

    return app
