import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.middleware")

# ──────────────────────────────────────────────
# Request Logging Middleware
# ──────────────────────────────────────────────

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs one structured JSON entry per HTTP request.

    Emitted fields:
        request_id, method, path, status_code, duration_ms

    The middleware also:
    - Accepts an inbound ``X-Request-ID`` header (or generates a UUID).
    - Echoes the ``X-Request-ID`` back on the response.

    Log levels by status-code range:
        2xx  → INFO
        3xx  → INFO
        4xx  → WARNING
        5xx  → ERROR
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # ── Request ID ──
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex

        # ── Timing ──
        start = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        # ── Choose log level based on status code ──
        status = response.status_code
        if status >= 500:
            log_level = logging.ERROR
        elif status >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        # ── Structured log entry ──
        logger.log(
            log_level,
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status,
                "duration_ms": duration_ms,
            },
        )

        # ── Echo request ID to caller ──
        response.headers["X-Request-ID"] = str(request_id)

        return response
