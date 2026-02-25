"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logger import get_logger, setup_logging

settings = get_settings()

# Initialize logging before anything else
setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    # Startup: ensure Qdrant collections exist
    from app.infrastructure.vector_store import ensure_collections, get_qdrant_client

    try:
        client = get_qdrant_client()
        ensure_collections(client)
        logger.info("Qdrant collections initialized")
    except Exception as e:
        logger.warning(f"Qdrant not available: {e}")
    yield
    logger.info("Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Middleware (order matters: first added = outermost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Trace-Id"],
)

from app.core.middleware import TraceMiddleware  # noqa: E402

app.add_middleware(TraceMiddleware)

# Register routers
from app.api.v1.auth import router as auth_router  # noqa: E402
from app.api.v1.growth import router as growth_router  # noqa: E402
from app.api.v1.interviews import router as interviews_router  # noqa: E402
from app.api.v1.jobs import router as jobs_router  # noqa: E402
from app.api.v1.knowledge import router as knowledge_router  # noqa: E402
from app.api.v1.quests import router as quests_router  # noqa: E402
from app.api.v1.resumes import router as resumes_router  # noqa: E402
from app.api.v1.skills import router as skills_router  # noqa: E402

app.include_router(auth_router, prefix="/api")
app.include_router(resumes_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(skills_router, prefix="/api")
app.include_router(interviews_router, prefix="/api")
app.include_router(quests_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(growth_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
