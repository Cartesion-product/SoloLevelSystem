"""Knowledge API endpoints."""

import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.knowledge import KnowledgeDocListResponse, KnowledgeDocResponse, KnowledgeDocStatusResponse, KnowledgeDocDetailResponse
from app.config import get_settings
from app.dependencies import get_current_user
from app.domain.interview.models import User
from app.domain.knowledge.repository import KnowledgeDocumentRepository
from app.infrastructure.database import get_db
from app.infrastructure.vector_store import KNOWLEDGE_CHUNKS_COLLECTION, delete_by_filter

settings = get_settings()
router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/upload", response_model=KnowledgeDocResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("tech_book"),
    domain_tags: str = Form(""),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document to the knowledge base."""
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "file")[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(content)

    tags = [t.strip() for t in domain_tags.split(",") if t.strip()] if domain_tags else None

    repo = KnowledgeDocumentRepository(db)
    doc = await repo.create(
        user_id=user.id,
        doc_name=file.filename or "Untitled",
        doc_type=doc_type,
        file_url=file_path,
        domain_tags=tags,
    )

    # Trigger async indexing
    from app.tasks.knowledge_indexing import index_document
    index_document.delay(str(doc.id), str(user.id), file_path, doc.doc_name)

    return KnowledgeDocResponse(
        id=str(doc.id),
        doc_name=doc.doc_name,
        doc_type=doc.doc_type,
        chunk_count=doc.chunk_count,
        status=doc.status,
        error_message=doc.error_message,
        domain_tags=doc.domain_tags,
        created_at=doc.created_at,
    )


@router.get("/documents/{doc_id}/status", response_model=KnowledgeDocStatusResponse)
async def get_document_status(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lightweight status polling endpoint for a single document."""
    repo = KnowledgeDocumentRepository(db)
    doc = await repo.get_by_id(uuid.UUID(doc_id))
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return KnowledgeDocStatusResponse(
        id=str(doc.id),
        status=doc.status,
        error_message=doc.error_message,
        chunk_count=doc.chunk_count,
    )


@router.get("/documents", response_model=KnowledgeDocListResponse)
async def list_documents(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = KnowledgeDocumentRepository(db)
    docs = await repo.get_by_user(user.id)
    return KnowledgeDocListResponse(
        documents=[
            KnowledgeDocResponse(
                id=str(d.id),
                doc_name=d.doc_name,
                doc_type=d.doc_type,
                chunk_count=d.chunk_count,
                status=d.status,
                error_message=d.error_message,
                domain_tags=d.domain_tags,
                created_at=d.created_at,
            )
            for d in docs
        ]
    )


@router.get("/documents/{doc_id}", response_model=KnowledgeDocDetailResponse)
async def get_document_detail(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get document details including extracted text chunks."""
    repo = KnowledgeDocumentRepository(db)
    doc = await repo.get_by_id(uuid.UUID(doc_id))
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Get chunks from vector store if processing finished
    from app.infrastructure.vector_store import get_chunks_by_doc_id
    from app.api.schemas.knowledge import KnowledgeChunkResponse
    
    chunks = []
    if doc.status == "ready":
        try:
            q_chunks = get_chunks_by_doc_id(KNOWLEDGE_CHUNKS_COLLECTION, doc_id)
            for chunk in q_chunks:
                payload = chunk.get("payload", {})
                chunks.append(
                    KnowledgeChunkResponse(
                        id=chunk["id"],
                        content=payload.get("content", ""),
                        source_type=payload.get("source_type"),
                    )
                )
        except Exception as e:
            # If Qdrant is down or throws error, we just return empty chunks
            import logging
            logging.getLogger(__name__).warning("Failed to fetch chunks from Qdrant: %s", e)

    return KnowledgeDocDetailResponse(
        document=KnowledgeDocResponse(
            id=str(doc.id),
            doc_name=doc.doc_name,
            doc_type=doc.doc_type,
            chunk_count=doc.chunk_count,
            status=doc.status,
            error_message=doc.error_message,
            domain_tags=doc.domain_tags,
            created_at=doc.created_at,
        ),
        chunks=chunks
    )


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = KnowledgeDocumentRepository(db)
    doc = await repo.get_by_id(uuid.UUID(doc_id))
    if not doc or doc.user_id != user.id:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete vectors from Qdrant
    try:
        delete_by_filter(KNOWLEDGE_CHUNKS_COLLECTION, {"doc_id": doc_id})
    except Exception:
        pass

    await repo.delete(uuid.UUID(doc_id))
