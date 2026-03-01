"""Knowledge document indexing async task."""

import asyncio
import logging
import uuid

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


_shared_loop = None

def _run_async(coro):
    """Run an async coroutine in a shared event loop for Celery sync workers."""
    global _shared_loop
    if _shared_loop is None or _shared_loop.is_closed():
        import asyncio
        _shared_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_shared_loop)
    return _shared_loop.run_until_complete(coro)


@celery_app.task(name="knowledge.index_document", bind=True, max_retries=2)
def index_document(self, doc_id: str, user_id: str, file_path: str, doc_name: str):
    """Parse, chunk, and vectorize a knowledge document."""
    logger.info("Starting indexing for doc_id=%s, doc_name=%s", doc_id, doc_name)
    try:
        _run_async(_index_document_async(doc_id, user_id, file_path, doc_name))
        logger.info("Indexing completed successfully for doc_id=%s", doc_id)
    except Exception as exc:
        logger.exception("Indexing task failed for doc_id=%s: %s", doc_id, exc)
        # Update status to failed with error message
        _run_async(_mark_failed(doc_id, str(exc)))
        raise


async def _mark_failed(doc_id: str, error_msg: str):
    """Mark a document as failed with an error message."""
    from sqlalchemy import select

    from app.domain.knowledge.models import KnowledgeDocument
    from app.domain.interview.models import User  # noqa: F401
    from app.infrastructure.database import async_session_factory

    async with async_session_factory() as db:
        result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == uuid.UUID(doc_id))
        )
        doc = result.scalar_one_or_none()
        if doc:
            doc.status = "failed"
            doc.error_message = error_msg[:1000]  # Truncate to avoid huge messages
            await db.commit()


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

    # Ensure User model is added to SQLAlchemy metadata before querying
    from app.domain.interview.models import User  # noqa: F401

    async with async_session_factory() as db:
        # Load document record
        result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == uuid.UUID(doc_id))
        )
        doc = result.scalar_one_or_none()
        if not doc:
            logger.warning("Document not found in DB: doc_id=%s", doc_id)
            return

        # Step 1: Read and parse file
        doc.status = "parsing"
        await db.commit()
        logger.info("[doc_id=%s] Parsing file: %s", doc_id, file_path)
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            raw_text = parse_file(file_bytes, doc_name)
        except Exception as exc:
            doc.status = "failed"
            doc.error_message = f"文件解析失败: {exc}"
            await db.commit()
            logger.error("[doc_id=%s] File parsing failed: %s", doc_id, exc)
            return

        # Step 2: Chunk text
        doc.status = "chunking"
        await db.commit()
        chunks = _chunk_text(raw_text, chunk_size=500, overlap=50)
        if not chunks:
            doc.status = "failed"
            doc.error_message = "文件内容为空，无法提取有效文本"
            await db.commit()
            logger.warning("[doc_id=%s] No chunks extracted from file", doc_id)
            return

        logger.info("[doc_id=%s] Extracted %d chunks", doc_id, len(chunks))

        # Step 3: Generate embeddings
        doc.status = "vectorizing"
        await db.commit()
        logger.info("[doc_id=%s] Generating embeddings...", doc_id)
        try:
            embedding = get_embedding_provider()
            vectors = await embedding.embed(chunks)
        except Exception as exc:
            doc.status = "failed"
            doc.error_message = f"向量化失败: {exc}"
            await db.commit()
            logger.error("[doc_id=%s] Embedding failed: %s", doc_id, exc)
            return

        # Step 4: Store in Qdrant
        doc.status = "storing"
        await db.commit()
        logger.info("[doc_id=%s] Storing %d vectors in Qdrant...", doc_id, len(vectors))
        try:
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
        except Exception as exc:
            doc.status = "failed"
            doc.error_message = f"向量存储失败: {exc}"
            await db.commit()
            logger.error("[doc_id=%s] Qdrant upsert failed: %s", doc_id, exc)
            return

        # Step 5: Mark success
        doc.chunk_count = len(chunks)
        doc.status = "ready"
        doc.error_message = None
        await db.commit()
        logger.info("[doc_id=%s] Indexing complete: %d chunks stored", doc_id, len(chunks))


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
