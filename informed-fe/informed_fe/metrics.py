import threading
from prometheus_client import Counter, Histogram, start_http_server

from informed_fe.config.logging import get_logger

logger = get_logger(__name__)

BACKEND_API_REQUESTS = Counter(
    "backend_api_requests_total",
    "Total number of requests to the backend API",
)

BACKEND_API_ERRORS = Counter(
    "backend_api_errors_total",
    "Total number of failed backend API requests",
    labelnames=["error_type"],
)

BACKEND_API_DURATION = Histogram(
    "backend_api_duration_seconds",
    "Time spent waiting for backend API responses",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
)

IMAGE_UPLOADS = Counter(
    "image_uploads_total",
    "Total number of images uploaded by users",
)

IMAGE_SIZE_BYTES = Histogram(
    "image_size_bytes",
    "Size of uploaded images in bytes",
    buckets=[10_000, 50_000, 100_000, 500_000, 1_000_000, 5_000_000, 10_000_000],
)

_metrics_server_started = False
_metrics_server_lock = threading.Lock()


def start_metrics_server(port: int = 9041) -> None:
    global _metrics_server_started

    with _metrics_server_lock:
        if _metrics_server_started:
            return

        try:
            start_http_server(port)
            _metrics_server_started = True
            logger.info(f"Prometheus metrics server started on port {port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {e}")
