"""Resume request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ResumeResponse(BaseModel):
    id: str
    title: str | None = None
    template_type: str | None = None
    is_default: bool = False
    parsed_data: dict[str, Any] = {}
    parsing_status: str = "completed"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResumeUpdate(BaseModel):
    title: str | None = None
    template_type: str | None = None
    parsed_data: dict[str, Any] | None = None


class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]
