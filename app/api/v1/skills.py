"""Skill tree API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.skills import RebuildRequest, SkillNodeResponse, SkillTreeResponse
from app.dependencies import get_current_user
from app.domain.capability.repository import SkillAdviceRepository, SkillTreeRepository
from app.domain.capability.service import rebuild_skill_tree
from app.domain.interview.models import User
from app.domain.interview.repository import ResumeRepository
from app.infrastructure.database import get_db
from app.infrastructure.llm_provider import get_llm_provider

router = APIRouter(prefix="/skills", tags=["skills"])


def _skills_to_response(skills, advice=None) -> SkillTreeResponse:
    return SkillTreeResponse(
        skills=[
            SkillNodeResponse(
                id=str(s.id),
                skill_name=s.skill_name,
                parent_skill_id=str(s.parent_skill_id) if s.parent_skill_id else None,
                proficiency_score=s.proficiency_score,
                evaluation_comment=s.evaluation_comment,
                source_type=s.source_type,
                focus_status=s.focus_status,
                assess_count=s.assess_count,
                last_assessed_at=s.last_assessed_at,
            )
            for s in skills
        ],
        strength_advice=advice.strength_advice if advice else None,
        weakness_advice=advice.weakness_advice if advice else None,
    )


@router.get("/tree", response_model=SkillTreeResponse)
async def get_skill_tree(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = SkillTreeRepository(db)
    skills = await repo.get_by_user(user.id)
    advice = await SkillAdviceRepository(db).get_by_user(user.id)
    return _skills_to_response(skills, advice)


@router.post("/rebuild", response_model=SkillTreeResponse)
async def rebuild_skill_tree_endpoint(
    body: RebuildRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rebuild skill tree from an existing resume's parsed data."""
    resume_repo = ResumeRepository(db)
    resume = await resume_repo.get_by_id(uuid.UUID(body.resume_id))
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not resume.parsed_data:
        raise HTTPException(status_code=400, detail="Resume has no parsed data")

    llm = get_llm_provider()
    await rebuild_skill_tree(db, user.id, resume.parsed_data, llm)

    skill_repo = SkillTreeRepository(db)
    skills = await skill_repo.get_by_user(user.id)
    advice = await SkillAdviceRepository(db).get_by_user(user.id)
    return _skills_to_response(skills, advice)
