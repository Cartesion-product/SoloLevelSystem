"""Redis async client wrapper."""

import json
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

redis_client = aioredis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


async def get_redis() -> aioredis.Redis:
    return redis_client


async def cache_set(key: str, value: Any, ttl_seconds: int | None = None) -> None:
    """Set a value in Redis cache, auto-serializing dicts/lists to JSON."""
    data = json.dumps(value) if isinstance(value, (dict, list)) else value
    if ttl_seconds:
        await redis_client.setex(key, ttl_seconds, data)
    else:
        await redis_client.set(key, data)


async def cache_get(key: str) -> Any:
    """Get a value from Redis cache, auto-deserializing JSON strings."""
    data = await redis_client.get(key)
    if data is None:
        return None
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return data


async def cache_delete(key: str) -> None:
    await redis_client.delete(key)


async def cache_set_list(key: str, values: list[str], ttl_seconds: int | None = None) -> None:
    """Store a list in Redis."""
    pipe = redis_client.pipeline()
    await pipe.delete(key)
    if values:
        await pipe.rpush(key, *values)
    if ttl_seconds:
        await pipe.expire(key, ttl_seconds)
    await pipe.execute()


async def cache_get_list(key: str) -> list[str]:
    return await redis_client.lrange(key, 0, -1)
