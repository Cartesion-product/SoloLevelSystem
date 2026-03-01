"""v2 Workspace read-only API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user
from app.domain.interview.models import User
from app.domain.workspace.service import WorkspaceManager
from app.infrastructure.database import get_db
from app.infrastructure.mongodb import get_mongo_db

router = APIRouter(prefix="/v2/workspace", tags=["v2-workspace"])


class SkillRadarEntryResponse(BaseModel):
    skill_name: str
    score: float
    source: str = ""
    assess_count: int = 0


class SkillRadarResponse(BaseModel):
    entries: list[SkillRadarEntryResponse] = Field(default_factory=list)


class WeakPointResponse(BaseModel):
    skill_name: str
    severity: str = "medium"
    description: str = ""
    recommended_action: str = ""
    resolved: bool = False


class ProfileResponse(BaseModel):
    user_id: str
    display_name: str = ""
    total_sessions: int = 0
    preferred_mode: str = "technical"


class SessionRecordResponse(BaseModel):
    session_id: str
    mode: str
    target_company: str | None = None
    overall_score: float = 0.0
    round_count: int = 0
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class TrainingPlanResponse(BaseModel):
    plan_id: str | None = None
    mode: str = ""
    target_topics: list[str] = Field(default_factory=list)
    focus_weak_points: list[str] = Field(default_factory=list)
    strategy_notes: str = ""


def _get_workspace_manager() -> WorkspaceManager:
    db = get_mongo_db()
    return WorkspaceManager(db)


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get workspace profile overview."""
    manager = _get_workspace_manager()

    # Auto-initialize from v1 if needed
    try:
        await manager.initialize_from_v1(str(user.id), db)
    except Exception:
        pass

    profile = await manager.repo.get_profile(str(user.id))
    if not profile:
        return ProfileResponse(user_id=str(user.id))

    return ProfileResponse(
        user_id=profile.user_id,
        display_name=profile.display_name,
        total_sessions=profile.total_sessions,
        preferred_mode=profile.preferred_mode,
    )


@router.get("/skill-radar", response_model=SkillRadarResponse)
async def get_skill_radar(
    user: User = Depends(get_current_user),
):
    """Get skill radar data."""
    manager = _get_workspace_manager()
    radar = await manager.repo.get_skill_radar(str(user.id))
    if not radar:
        return SkillRadarResponse()

    return SkillRadarResponse(
        entries=[
            SkillRadarEntryResponse(
                skill_name=e.skill_name,
                score=e.score,
                source=e.source,
                assess_count=e.assess_count,
            )
            for e in radar.entries
        ]
    )


@router.get("/weak-points", response_model=list[WeakPointResponse])
async def get_weak_points(
    user: User = Depends(get_current_user),
):
    """Get list of weak points."""
    manager = _get_workspace_manager()
    weak_points = await manager.repo.get_weak_points(str(user.id))

    return [
        WeakPointResponse(
            skill_name=wp.skill_name,
            severity=wp.severity,
            description=wp.description,
            recommended_action=wp.recommended_action,
            resolved=wp.resolved,
        )
        for wp in weak_points
    ]


@router.get("/sessions", response_model=list[SessionRecordResponse])
async def get_sessions(
    user: User = Depends(get_current_user),
):
    """Get session history from workspace."""
    manager = _get_workspace_manager()
    sessions = await manager.repo.get_sessions(str(user.id))

    return [
        SessionRecordResponse(
            session_id=s.session_id,
            mode=s.mode,
            target_company=s.target_company,
            overall_score=s.overall_score,
            round_count=s.round_count,
            strengths=s.strengths,
            weaknesses=s.weaknesses,
        )
        for s in sessions
    ]


@router.get("/plan", response_model=TrainingPlanResponse)
async def get_plan(
    user: User = Depends(get_current_user),
):
    """Get the latest training plan."""
    manager = _get_workspace_manager()
    plan = await manager.repo.get_latest_plan(str(user.id))
    if not plan:
        return TrainingPlanResponse()

    return TrainingPlanResponse(
        plan_id=plan.plan_id,
        mode=plan.mode,
        target_topics=plan.target_topics,
        focus_weak_points=plan.focus_weak_points,
        strategy_notes=plan.strategy_notes,
    )
