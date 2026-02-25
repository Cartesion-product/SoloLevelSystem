"""Qdrant vector store client wrapper."""

import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.config import get_settings

settings = get_settings()

KNOWLEDGE_CHUNKS_COLLECTION = "knowledge_chunks"
CONVERSATION_MEMORY_COLLECTION = "conversation_memory"


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY,
    )


def ensure_collections(client: QdrantClient | None = None) -> None:
    """Create Qdrant collections if they don't exist."""
    if client is None:
        client = get_qdrant_client()

    dim = settings.EMBEDDING_DIMENSION

    for collection_name in [KNOWLEDGE_CHUNKS_COLLECTION, CONVERSATION_MEMORY_COLLECTION]:
        existing = [c.name for c in client.get_collections().collections]
        if collection_name not in existing:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )


def upsert_vectors(
    collection: str,
    ids: list[str],
    vectors: list[list[float]],
    payloads: list[dict[str, Any]],
    client: QdrantClient | None = None,
) -> None:
    if client is None:
        client = get_qdrant_client()

    points = [
        PointStruct(id=uid, vector=vec, payload=payload)
        for uid, vec, payload in zip(ids, vectors, payloads)
    ]
    client.upsert(collection_name=collection, points=points)


def search_vectors(
    collection: str,
    query_vector: list[float],
    limit: int = 5,
    filter_conditions: dict[str, Any] | None = None,
    client: QdrantClient | None = None,
) -> list[dict]:
    if client is None:
        client = get_qdrant_client()

    qdrant_filter = None
    if filter_conditions:
        must = [
            FieldCondition(key=k, match=MatchValue(value=v))
            for k, v in filter_conditions.items()
        ]
        qdrant_filter = Filter(must=must)

    results = client.query_points(
        collection_name=collection,
        query=query_vector,
        limit=limit,
        query_filter=qdrant_filter,
        with_payload=True,
    )

    return [
        {"id": str(hit.id), "score": hit.score, "payload": hit.payload}
        for hit in results.points
    ]


def delete_by_filter(
    collection: str,
    filter_conditions: dict[str, Any],
    client: QdrantClient | None = None,
) -> None:
    if client is None:
        client = get_qdrant_client()

    must = [
        FieldCondition(key=k, match=MatchValue(value=v))
        for k, v in filter_conditions.items()
    ]
    client.delete(
        collection_name=collection,
        points_selector=Filter(must=must),
    )
