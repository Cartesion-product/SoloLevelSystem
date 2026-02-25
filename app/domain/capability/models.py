"""Capability domain models: skill_tree."""

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class SkillTree(Base):
    __tablename__ = "skill_tree"
    __table_args__ = (
        Index("idx_skill_user", "user_id"),
        Index("idx_skill_gap", "user_id", "source_type"),
        Index("idx_skill_focus", "user_id", "focus_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_skill_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("skill_tree.id"))
    proficiency_score: Mapped[int] = mapped_column(SmallInteger, default=0)
    evaluation_comment: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(50), default="resume_claimed")
    focus_status: Mapped[str] = mapped_column(String(50), default="dormant")
    assess_count: Mapped[int] = mapped_column(Integer, default=0)
    last_assessed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class SkillAdvice(Base):
    __tablename__ = "skill_advice"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    strength_advice: Mapped[str | None] = mapped_column(Text)
    weakness_advice: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
