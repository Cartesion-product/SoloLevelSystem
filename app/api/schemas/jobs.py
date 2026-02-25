"""Target job request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    company_name: str | None = None
    position_name: str = Field(..., min_length=1, max_length=255)
    jd_text: str = Field(..., min_length=1)


class JobResponse(BaseModel):
    id: str
    company_name: str | None = None
    position_name: str
    jd_text: str
    parsed_requirements: dict[str, Any] | None = None
    is_default: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class JobUpdate(BaseModel):
    company_name: str | None = None
    position_name: str | None = None
    jd_text: str | None = None
    parsed_requirements: dict[str, Any] | None = None


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
