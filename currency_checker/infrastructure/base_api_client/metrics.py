from prometheus_client import Summary


HTTP_REQUEST_DURATION_SECONDS = Summary(
    name="cme_api_client_http_request_duration_seconds",
    documentation="",
    labelnames=(
        "api_service_name", "client_name", "base_uri", "path", "method", "response_status"
    ),
)
