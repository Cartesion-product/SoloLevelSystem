"""Interview session request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class InterviewStartRequest(BaseModel):
    resume_id: str | None = None
    job_id: str | None = None
    max_questions: int = 8


class InterviewChatRequest(BaseModel):
    message: str


class InterviewSessionResponse(BaseModel):
    id: str
    status: str
    session_type: str
    question_count: int
    first_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class InterviewReportResponse(BaseModel):
    session_id: str
    status: str
    summary: dict[str, Any] | None = None
    question_count: int
    duration_seconds: int | None = None
    created_at: datetime
    completed_at: datetime | None = None
