"""Knowledge document request/response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class KnowledgeDocResponse(BaseModel):
    id: str
    doc_name: str
    doc_type: str | None = None
    chunk_count: int = 0
    status: Literal["pending", "processing", "parsing", "chunking", "vectorizing", "storing", "ready", "failed"] = "pending"
    error_message: str | None = None
    domain_tags: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeDocStatusResponse(BaseModel):
    id: str
    status: Literal["pending", "processing", "parsing", "chunking", "vectorizing", "storing", "ready", "failed"]
    error_message: str | None = None
    chunk_count: int = 0


class KnowledgeDocListResponse(BaseModel):
    documents: list[KnowledgeDocResponse]


class KnowledgeChunkResponse(BaseModel):
    id: str
    content: str
    source_type: str | None = None


class KnowledgeDocDetailResponse(BaseModel):
    document: KnowledgeDocResponse
    chunks: list[KnowledgeChunkResponse]
