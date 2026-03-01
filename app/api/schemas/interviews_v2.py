"""v2 Interview session request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class InterviewStartV2Request(BaseModel):
    resume_id: str | None = None
    job_id: str | None = None
    mode: str = Field(default="technical", pattern="^(behavioral|technical|system_design|hr)$")
    target_company: str | None = None
    max_rounds: int = Field(default=5, ge=1, le=20)


class InterviewChatV2Request(BaseModel):
    message: str


class TrainingPlanResponse(BaseModel):
    plan_id: str | None = None
    target_topics: list[str] = Field(default_factory=list)
    focus_weak_points: list[str] = Field(default_factory=list)
    strategy_notes: str = ""
    round_plan: list[dict[str, Any]] = Field(default_factory=list)


class InterviewSessionV2Response(BaseModel):
    id: str
    status: str
    mode: str
    target_company: str | None = None
    question_count: int = 0
    max_rounds: int = 5
    first_message: str | None = None
    training_plan: TrainingPlanResponse | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class RoundScoreResponse(BaseModel):
    round: int = 0
    score: float = 0.0
    feedback: str = ""
    key_points_hit: list[str] = Field(default_factory=list)
    key_points_missed: list[str] = Field(default_factory=list)


class InterviewReportV2Response(BaseModel):
    session_id: str
    status: str
    mode: str
    target_company: str | None = None
    summary: dict[str, Any] | None = None
    round_scores: list[RoundScoreResponse] = Field(default_factory=list)
    question_count: int = 0
    created_at: datetime
    completed_at: datetime | None = None
