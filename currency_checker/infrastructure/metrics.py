import logging
import os
from ssl import SSLContext
from typing import Any, Optional

from aiohttp import hdrs, web
from prometheus_async.aio.web import MetricsHTTPServer, _choose_generator
from prometheus_client import REGISTRY, CollectorRegistry, multiprocess


def server_stats(request: web.Request) -> web.Response:
    """
    Modified copy of prometheus_async.aio.web.server_stats.
    Added support of multiprocess mode,
    https://github.com/prometheus/client_python#multiprocess-mode-eg-gunicorn.

    Return a web response with the plain text version of the metrics.

    :rtype: :class:`aiohttp.web.Response`
    """
    if os.environ.get('PROMETHEUS_MULTIPROC_DIR'):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = REGISTRY

    generate, content_type = _choose_generator(request.headers.get(hdrs.ACCEPT))

    rsp = web.Response(body=generate(registry))
    # This is set separately because aiohttp complains about `;` in
    # content_type thinking it means there's also a charset.
    # cf. https://github.com/aio-libs/aiohttp/issues/2197
    rsp.content_type = content_type

    return rsp


async def get_ping_response(request: web.Request) -> web.Response:
    logging.debug('Pong for %s', request.remote)
    return web.Response(text='200 VERY OK')


async def get_metric_response(request: web.Request) -> web.Response:
    logging.debug('Show metrics for %s', request.remote)
    return server_stats(request)


async def start_metric_server(
    *,
    addr: str = "",
    port: int = 0,
    ssl_ctx: Optional[SSLContext] = None,
    service_discovery: Optional[Any] = None
) -> MetricsHTTPServer:
    """
    Start an HTTP(S) server on *addr*:*port*.

    If *ssl_ctx* is set, use TLS.

    :param str addr: Interface to listen on. Leaving empty will listen on all
        interfaces.
    :param int port: Port to listen on.
    :param ssl.SSLContext ssl_ctx: TLS settings
    :param service_discovery: see :ref:`sd`

    :rtype: MetricsHTTPServer
    """
    app = web.Application()
    app.router.add_get('/metrics', get_metric_response)
    app.router.add_get('/ping', get_ping_response)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, addr, port, ssl_context=ssl_ctx)
    await site.start()

    ms = MetricsHTTPServer.from_server(
        runner=runner, app=app, https=ssl_ctx is not None
    )
    if service_discovery is not None:
        ms._deregister = await service_discovery.register(ms)

    logging.info('Metric server run on %s port', port)
    return ms
