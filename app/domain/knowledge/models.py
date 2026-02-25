"""Knowledge domain models: knowledge_documents."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    doc_name: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str | None] = mapped_column(String(50))
    file_url: Mapped[str | None] = mapped_column(Text)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="processing")
    domain_tags: Mapped[list[str] | None] = mapped_column(ARRAY(Text))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
