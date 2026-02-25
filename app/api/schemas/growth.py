"""Growth dashboard request/response schemas."""

from typing import Any

from pydantic import BaseModel


class GrowthDashboardResponse(BaseModel):
    skill_overview: list[dict[str, Any]]
    quest_progress: dict[str, int]
    daily_motivation: str | None = None
    confidence_score: float | None = None
    interview_history: list[dict[str, Any]]
