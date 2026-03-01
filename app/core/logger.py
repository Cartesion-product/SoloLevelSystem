"""Centralized logging configuration.

Log format:
    2026-03-01 10:44:55.123 【trace_id】 LEVEL  logger_name - message

Directory layout (app and celery logs completely isolated):
    logs/
    ├── app/
    │   ├── app.log           ← current day (tail -f this)
    │   ├── 2026-02-28.log    ← rotated by date
    │   ├── 2026-02-27.log
    │   └── ...
    └── celery/
        ├── celery.log
        ├── 2026-02-28.log
        └── ...

Usage:
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")
"""

import logging
import os
import sys
from contextvars import ContextVar
from logging.handlers import TimedRotatingFileHandler

from app.config import BASE_DIR

LOG_DIR = BASE_DIR / "logs"

# ---------------------------------------------------------------------------
# Trace ID context (async-safe via ContextVar)
# ---------------------------------------------------------------------------
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")


def get_trace_id() -> str:
    return trace_id_var.get()


def set_trace_id(tid: str) -> None:
    trace_id_var.set(tid)


# ---------------------------------------------------------------------------
# Custom formatter
# ---------------------------------------------------------------------------
class TraceFormatter(logging.Formatter):
    """Inject trace_id into every log line."""

    def format(self, record: logging.LogRecord) -> str:
        record.trace_id = get_trace_id()  # type: ignore[attr-defined]
        return super().format(record)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
_FMT = "%(asctime)s.%(msecs)03d 【%(trace_id)s】 %(levelname)-5s %(name)s - %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_initialized = False

# Third-party loggers that are too noisy at INFO/DEBUG
_NOISY_LOGGERS = (
    "uvicorn.access",
    "httpcore",
    "httpx",
    "openai",
    "asyncio",
    "python_multipart.multipart",
    "watchfiles.main",
    "pymongo",
    "pymongo.topology",
    "pymongo.connection",
)


def _date_namer(default_name: str) -> str:
    """Rename rotated log file from '{base}.log.2026-03-01' to '2026-03-01.log'.

    This makes the log directory browsable by date at a glance.
    """
    # default_name = "D:/…/logs/app/app.log.2026-03-01"
    dir_name = os.path.dirname(default_name)
    base_name = os.path.basename(default_name)  # "app.log.2026-03-01"
    # Extract the date suffix (everything after the last dot-separated date pattern)
    parts = base_name.rsplit(".", 1)  # ["app.log", "2026-03-01"]
    if len(parts) == 2:
        return os.path.join(dir_name, f"{parts[1]}.log")
    return default_name  # fallback: don't break if format is unexpected


def setup_logging(level: str = "INFO", process_name: str = "app") -> None:
    """Initialize root logger with console + daily rotating file handlers.

    Args:
        level: Log level string (DEBUG / INFO / WARNING / ERROR).
        process_name: Determines log subdirectory and base file name.
                      "app"    -> logs/app/app.log
                      "celery" -> logs/celery/celery.log
    """
    global _initialized
    if _initialized:
        return
    _initialized = True

    # Each process gets its own subdirectory
    process_log_dir = LOG_DIR / process_name
    process_log_dir.mkdir(parents=True, exist_ok=True)

    log_level = getattr(logging, level.upper(), logging.INFO)
    formatter = TraceFormatter(fmt=_FMT, datefmt=_DATE_FMT)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(log_level)

    # --- Windows stdout UTF-8 fix ---
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # --- Console handler ---
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # --- File handler (daily rotation, 30 days retention) ---
    log_file = process_log_dir / f"{process_name}.log"
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.namer = _date_namer
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # --- Suppress noisy third-party loggers ---
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    # --- SQLAlchemy: keep at INFO even in DEBUG to avoid per-query spam ---
    sa_logger = logging.getLogger("sqlalchemy.engine")
    sa_logger.setLevel(logging.INFO if log_level == logging.DEBUG else logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Call setup_logging() first in main."""
    return logging.getLogger(name)
