"""Target job API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.jobs import JobCreateRequest, JobListResponse, JobResponse, JobUpdate
from app.dependencies import get_current_user
from app.domain.interview.models import TargetJob, User
from app.domain.interview.repository import TargetJobRepository
from app.domain.interview.service import parse_jd_with_llm
from app.infrastructure.database import get_db
from app.infrastructure.llm_provider import get_llm_provider

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _to_response(j: TargetJob) -> JobResponse:
    return JobResponse(
        id=str(j.id),
        company_name=j.company_name,
        position_name=j.position_name,
        jd_text=j.jd_text,
        parsed_requirements=j.parsed_requirements,
        is_default=j.is_default,
        created_at=j.created_at,
    )


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: JobCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a target job and parse JD with LLM."""
    llm = get_llm_provider()
    parsed_requirements = await parse_jd_with_llm(body.jd_text, llm)

    repo = TargetJobRepository(db)
    job = await repo.create(
        user_id=user.id,
        company_name=body.company_name,
        position_name=body.position_name,
        jd_text=body.jd_text,
        parsed_requirements=parsed_requirements,
    )
    return _to_response(job)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = TargetJobRepository(db)
    jobs = await repo.get_by_user(user.id)
    return JobListResponse(jobs=[_to_response(j) for j in jobs])


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = TargetJobRepository(db)
    job = await repo.get_by_id(uuid.UUID(job_id))
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return _to_response(job)


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    body: JobUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = TargetJobRepository(db)
    job = await repo.get_by_id(uuid.UUID(job_id))
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    updates = body.model_dump(exclude_none=True)
    job = await repo.update(uuid.UUID(job_id), **updates)
    return _to_response(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = TargetJobRepository(db)
    job = await repo.get_by_id(uuid.UUID(job_id))
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    await repo.delete(uuid.UUID(job_id))


@router.post("/{job_id}/set-default", response_model=JobResponse)
async def set_default_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = TargetJobRepository(db)
    job = await repo.get_by_id(uuid.UUID(job_id))
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    job = await repo.set_default(user.id, uuid.UUID(job_id))
    return _to_response(job)
