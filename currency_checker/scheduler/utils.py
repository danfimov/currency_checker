import asyncio

from prometheus_async.aio.web import MetricsHTTPServer

from currency_checker.infrastructure.metrics import start_metric_server


def run_metrics_server(metrics_port: int | None) -> MetricsHTTPServer | None:
    server = None
    if metrics_port:
        server = asyncio.run(start_metric_server(port=metrics_port))
    return server
