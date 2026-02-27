import json
import logging
import os
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

# ──────────────────────────────────────────────
# Structured JSON Formatter
# ──────────────────────────────────────────────

class JSONFormatter(logging.Formatter):
    """Outputs each log record as a single JSON line.

    Standard fields emitted for *every* record:
        timestamp, level, message

    Middleware-injected fields (present only on request logs):
        request_id, method, path, status_code, duration_ms
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Middleware attaches these via `extra={...}`
        for field in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
        ):
            value = getattr(record, field, None)
            if value is not None:
                log_entry[field] = value

        # Allow any other extra keys that services might pass
        # (e.g. model, tokens, latency)
        for key, value in record.__dict__.items():
            if key not in log_entry and key not in logging.LogRecord(
                "", 0, "", 0, "", (), None
            ).__dict__:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


# ──────────────────────────────────────────────
# Bootstrap
# ──────────────────────────────────────────────

_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "app.log")

# Rotation defaults
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB per file
_BACKUP_COUNT = 5              # keep 5 rotated copies


# App logger name — all application code should use loggers under this namespace
# e.g.  logging.getLogger("app.middleware"), logging.getLogger("app.scraper")
APP_LOGGER_NAME = "app"


def setup_logging(level: str = "INFO") -> None:
    """Configure the *app* logger with a rotating-file JSON handler.

    Only loggers under the ``app.*`` namespace write to ``logs/app.log``.
    Uvicorn / WatchFiles / third-party loggers are **not** attached, so
    writing to the log file will never trigger the dev-server file watcher.

    Call once at app startup (before any request is served).
    ``level`` accepts standard names: DEBUG, INFO, WARNING, ERROR, CRITICAL.
    """

    os.makedirs(_LOG_DIR, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    json_formatter = JSONFormatter()

    # ── File handler (rotating) ──
    file_handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(json_formatter)

    # ── App logger (NOT root) ──
    app_logger = logging.getLogger(APP_LOGGER_NAME)
    app_logger.setLevel(numeric_level)
    app_logger.handlers.clear()           # avoid duplicate handlers on reload
    app_logger.addHandler(file_handler)
    app_logger.propagate = False          # don't bubble up to root / console

    app_logger.info("logging_initialized", extra={"log_level": level})
