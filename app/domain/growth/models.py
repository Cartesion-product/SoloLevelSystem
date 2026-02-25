"""Growth domain models: quest_log, user_psychology_profile, mood_log."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class QuestLog(Base):
    __tablename__ = "quest_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"))
    target_skill_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("skill_tree.id"))
    quest_title: Mapped[str] = mapped_column(String(255), nullable=False)
    quest_detail: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="generated")
    verification_method: Mapped[str | None] = mapped_column(String(50))
    due_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)


class UserPsychologyProfile(Base):
    __tablename__ = "user_psychology_profile"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    personality_tags: Mapped[list] = mapped_column(JSONB, default=list)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    resilience_score: Mapped[float] = mapped_column(Float, default=0.5)
    preferred_style: Mapped[str] = mapped_column(String(50), default="balanced")
    daily_motivation: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class MoodLog(Base):
    __tablename__ = "mood_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"))
    detected_mood: Mapped[str | None] = mapped_column(String(50))
    trigger_event: Mapped[str | None] = mapped_column(Text)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
