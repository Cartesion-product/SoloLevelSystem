"""Knowledge document request/response schemas."""

from datetime import datetime

from pydantic import BaseModel


class KnowledgeDocResponse(BaseModel):
    id: str
    doc_name: str
    doc_type: str | None = None
    chunk_count: int = 0
    status: str = "processing"
    domain_tags: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeDocListResponse(BaseModel):
    documents: list[KnowledgeDocResponse]
