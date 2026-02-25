"""Growth dashboard API endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.growth import GrowthDashboardResponse
from app.dependencies import get_current_user
from app.domain.capability.repository import SkillTreeRepository
from app.domain.growth.repository import PsychologyProfileRepository, QuestRepository
from app.domain.interview.models import User
from app.domain.interview.repository import InterviewSessionRepository
from app.infrastructure.database import get_db

router = APIRouter(prefix="/growth", tags=["growth"])


@router.get("/dashboard", response_model=GrowthDashboardResponse)
async def get_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get growth dashboard: skill overview, quest progress, motivation, interview history."""
    skill_repo = SkillTreeRepository(db)
    quest_repo = QuestRepository(db)
    profile_repo = PsychologyProfileRepository(db)
    session_repo = InterviewSessionRepository(db)

    # Skill overview (radar chart data)
    skills = await skill_repo.get_by_user(user.id)
    skill_overview = [
        {
            "name": s.skill_name,
            "score": s.proficiency_score,
            "source_type": s.source_type,
            "focus_status": s.focus_status,
            "parent_id": str(s.parent_skill_id) if s.parent_skill_id else None,
        }
        for s in skills
    ]

    # Quest progress summary
    all_quests = await quest_repo.get_by_user(user.id)
    quest_progress = {}
    for q in all_quests:
        quest_progress[q.status] = quest_progress.get(q.status, 0) + 1

    # Psychology profile
    profile = await profile_repo.get_by_user(user.id)
    daily_motivation = profile.daily_motivation if profile else None
    confidence_score = profile.confidence_score if profile else None

    # Interview history (last 10 sessions)
    sessions = await session_repo.get_by_user(user.id, limit=10)
    interview_history = [
        {
            "id": str(s.id),
            "status": s.status,
            "question_count": s.question_count,
            "overall_score": (s.summary or {}).get("overall_score"),
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]

    return GrowthDashboardResponse(
        skill_overview=skill_overview,
        quest_progress=quest_progress,
        daily_motivation=daily_motivation,
        confidence_score=confidence_score,
        interview_history=interview_history,
    )
