"""Knowledge domain service: hybrid retrieval."""

from app.infrastructure.embedding import get_embedding_provider
from app.infrastructure.vector_store import KNOWLEDGE_CHUNKS_COLLECTION, search_vectors


async def hybrid_search(
    query: str,
    user_id: str,
    limit: int = 5,
    doc_type: str | None = None,
) -> list[dict]:
    """Perform hybrid search: vector similarity + optional filter."""
    embedding = get_embedding_provider()
    query_vector = await embedding.embed_single(query)

    filters = {"user_id": user_id}
    if doc_type:
        filters["source_type"] = doc_type

    results = search_vectors(
        collection=KNOWLEDGE_CHUNKS_COLLECTION,
        query_vector=query_vector,
        limit=limit,
        filter_conditions=filters,
    )

    return results
