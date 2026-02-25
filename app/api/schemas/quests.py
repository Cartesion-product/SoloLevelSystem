"""Quest request/response schemas."""

from datetime import date, datetime

from pydantic import BaseModel


class QuestResponse(BaseModel):
    id: str
    quest_title: str
    quest_detail: str
    status: str = "generated"
    verification_method: str | None = None
    target_skill_id: str | None = None
    due_date: date | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class QuestListResponse(BaseModel):
    quests: list[QuestResponse]


class QuestStatusUpdate(BaseModel):
    status: str  # generated, in_progress, submitted, verified_pass, verified_fail
