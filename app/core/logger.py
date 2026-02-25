"""Centralized logging configuration.

Log format:
    2026-02-08 10:44:55.123 【trace_id】 LEVEL  logger_name - message

Usage:
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from app.config import BASE_DIR

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Trace ID context (thread-safe via ContextVar)
# ---------------------------------------------------------------------------
from contextvars import ContextVar

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
        record.trace_id = get_trace_id()
        return super().format(record)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
_FMT = "%(asctime)s.%(msecs)03d 【%(trace_id)s】 %(levelname)-5s %(name)s - %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_initialized = False


def setup_logging(level: str = "DEBUG") -> None:
    """Initialize root logger with console + daily rotating file handlers."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    log_level = getattr(logging, level.upper(), logging.DEBUG)
    formatter = TraceFormatter(fmt=_FMT, datefmt=_DATE_FMT)

    root = logging.getLogger()
    root.setLevel(log_level)

    # --- Console handler ---
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(formatter)
    root.addHandler(console)

    # --- File handler (daily rotation, 30 days retention) ---
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{today}.log"
    file_handler = TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.suffix = "%Y-%m-%d.log"
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Suppress noisy third-party loggers
    for name in (
        "uvicorn.access",
        "httpcore",
        "httpx",
        "openai",
        "asyncio",
        "python_multipart.multipart",
        "watchfiles.main",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)

    # SQLAlchemy: only show SQL in DEBUG mode, suppress duplicate uvicorn handler output
    sa_logger = logging.getLogger("sqlalchemy.engine")
    if log_level > logging.DEBUG:
        sa_logger.setLevel(logging.WARNING)
    else:
        sa_logger.setLevel(logging.INFO)
    # Prevent SQLAlchemy from propagating to root (avoids duplicate lines)
    sa_logger.propagate = False
    sa_handler = logging.StreamHandler(sys.stdout)
    sa_handler.setFormatter(formatter)
    sa_logger.addHandler(sa_handler)
    sa_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Call setup_logging() first in main."""
    return logging.getLogger(name)
