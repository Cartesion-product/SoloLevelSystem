"""Knowledge document indexing async task."""

import asyncio
import uuid

from app.tasks.celery_app import celery_app


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="knowledge.index_document")
def index_document(doc_id: str, user_id: str, file_path: str, doc_name: str):
    """Parse, chunk, and vectorize a knowledge document."""
    _run_async(_index_document_async(doc_id, user_id, file_path, doc_name))


async def _index_document_async(doc_id: str, user_id: str, file_path: str, doc_name: str):
    from sqlalchemy import select

    from app.domain.knowledge.models import KnowledgeDocument
    from app.infrastructure.database import async_session_factory
    from app.infrastructure.embedding import get_embedding_provider
    from app.infrastructure.file_parser import parse_file
    from app.infrastructure.vector_store import (
        KNOWLEDGE_CHUNKS_COLLECTION,
        upsert_vectors,
    )

    async with async_session_factory() as db:
        # Load document record
        result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == uuid.UUID(doc_id))
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return

        try:
            # Read file
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            raw_text = parse_file(file_bytes, doc_name)

            # Chunk text
            chunks = _chunk_text(raw_text, chunk_size=500, overlap=50)

            if not chunks:
                doc.status = "failed"
                await db.commit()
                return

            # Embed chunks
            embedding = get_embedding_provider()
            vectors = await embedding.embed(chunks)

            # Store in Qdrant
            ids = [str(uuid.uuid4()) for _ in chunks]
            payloads = [
                {
                    "user_id": user_id,
                    "doc_id": doc_id,
                    "content": chunk,
                    "source_type": doc.doc_type or "unknown",
                    "tags": doc.domain_tags or [],
                }
                for chunk in chunks
            ]

            upsert_vectors(KNOWLEDGE_CHUNKS_COLLECTION, ids, vectors, payloads)

            # Update document status
            doc.chunk_count = len(chunks)
            doc.status = "ready"

        except Exception:
            doc.status = "failed"

        await db.commit()


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    if not text.strip():
        return []

    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
        i += chunk_size - overlap

    return chunks
