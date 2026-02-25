"""Pytest fixtures for testing.

Uses a separate test database (solo_leveling_test) to avoid affecting production data.
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.infrastructure.database import Base, get_db

settings = get_settings()

# Build test DB URL: replace DB name with <original>_test
_base_url = settings.DATABASE_URL.rsplit("/", 1)[0]
_prod_db = settings.DATABASE_URL.rsplit("/", 1)[1]
_test_db_name = f"{_prod_db}_test"
TEST_DATABASE_URL = f"{_base_url}/{_test_db_name}"


# --------------- Create test DB at import time ---------------
def _ensure_test_db_exists():
    """Create the test database if it doesn't exist yet.

    Runs synchronously at module import time using a temporary event loop,
    BEFORE the async test engine is created. This avoids the template1
    locking issue that occurs when asyncpg pool connections race with
    CREATE DATABASE.
    """
    async def _create():
        engine = create_async_engine(
            f"{_base_url}/postgres",
            isolation_level="AUTOCOMMIT",
            pool_size=1,
            max_overflow=0,
        )
        try:
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db"),
                    {"db": _test_db_name},
                )
                if result.scalar() is None:
                    # Terminate other connections using template1 to avoid locking
                    await conn.execute(text(
                        "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                        "WHERE datname = 'template1' AND pid != pg_backend_pid()"
                    ))
                    await conn.execute(text(f'CREATE DATABASE "{_test_db_name}"'))
        finally:
            await engine.dispose()

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_create())
    finally:
        loop.close()


_ensure_test_db_exists()

# Now it's safe to create the test engine — DB is guaranteed to exist
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5, max_overflow=0)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test, drop after. Uses test DB only."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Delay app import so logging doesn't interfere
from app.main import app  # noqa: E402

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


# ---- Helper: authenticated client ----

@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    """Register a user and return a client with auth header set."""
    uid = uuid.uuid4().hex[:8]
    await client.post("/api/auth/register", json={
        "username": f"user_{uid}",
        "email": f"{uid}@test.com",
        "password": "test123456",
    })
    resp = await client.post("/api/auth/login", json={
        "email": f"{uid}@test.com",
        "password": "test123456",
    })
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


# ---- Mock LLM provider ----

@pytest.fixture
def mock_llm():
    """Return a mock LLM provider for tests that don't need real LLM calls."""
    mock = AsyncMock()
    mock.chat = AsyncMock(return_value='{"basic_info": {"name": "Test"}, "skills": {}, "projects": [], "work_experience": []}')
    mock.stream_chat = AsyncMock()
    return mock
