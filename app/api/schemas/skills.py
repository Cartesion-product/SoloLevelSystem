"""Skill tree request/response schemas."""

from datetime import datetime

from pydantic import BaseModel


class SkillNodeResponse(BaseModel):
    id: str
    skill_name: str
    parent_skill_id: str | None = None
    proficiency_score: int = 0
    evaluation_comment: str | None = None
    source_type: str = "resume_claimed"
    focus_status: str = "dormant"
    assess_count: int = 0
    last_assessed_at: datetime | None = None

    model_config = {"from_attributes": True}


class SkillTreeResponse(BaseModel):
    skills: list[SkillNodeResponse]
    strength_advice: str | None = None
    weakness_advice: str | None = None


class RebuildRequest(BaseModel):
    resume_id: str
