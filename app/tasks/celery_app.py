"""Celery application configuration."""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "solo_leveling",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

from celery.signals import setup_logging as celery_setup_logging, worker_ready

@celery_setup_logging.connect
def config_loggers(*args, **kwargs):
    """Intercept Celery's logging setup and replace with our own.

    Connecting to this signal tells Celery to skip its default logging config.
    However Celery's -l/--loglevel flag can still override handlers afterwards,
    so we also re-apply in worker_ready to guarantee our file handler survives.
    """
    from app.core.logger import setup_logging
    setup_logging(level=settings.LOG_LEVEL, process_name="celery")


@worker_ready.connect
def on_worker_ready(*args, **kwargs):
    """Re-apply our logging config after Celery has finished all its setup.

    This ensures the file handler (logs/celery/celery.log) is present even
    if Celery's -l flag or internal bootstrap overwrote root handlers.
    """
    from app.core.logger import setup_logging, _initialized
    import app.core.logger as _logger_mod
    # Reset the guard so setup_logging actually runs again
    _logger_mod._initialized = False
    setup_logging(level=settings.LOG_LEVEL, process_name="celery")

celery_app.autodiscover_tasks(["app.tasks"])

# Explicitly import tasks so they are registered
import app.tasks.knowledge_indexing  # noqa: F401
