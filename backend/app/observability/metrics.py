from time import perf_counter
from typing import Callable

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_LATENCY_SECONDS = Histogram(
    "app_request_latency_seconds",
    "Latency of app operations by operation name.",
    ["operation"],
)

REQUEST_ERRORS_TOTAL = Counter(
    "app_request_errors_total",
    "Total number of operation errors.",
    ["operation"],
)


def observe_latency(operation: str, started_at: float) -> None:
    REQUEST_LATENCY_SECONDS.labels(operation=operation).observe(perf_counter() - started_at)


def increment_error(operation: str) -> None:
    REQUEST_ERRORS_TOTAL.labels(operation=operation).inc()


def render_metrics() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST

