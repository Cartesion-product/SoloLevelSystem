"""MongoDB async client using motor."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_mongo_db() -> AsyncIOMotorDatabase:
    """Return the MongoDB database instance. Must call init_mongo() first."""
    if _db is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongo() first.")
    return _db


async def init_mongo() -> None:
    """Initialize the MongoDB connection."""
    global _client, _db
    _client = AsyncIOMotorClient(settings.MONGO_URL)
    _db = _client[settings.MONGO_DB_NAME]


async def close_mongo() -> None:
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
