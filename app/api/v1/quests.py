"""Quest API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.quests import QuestListResponse, QuestResponse, QuestStatusUpdate
from app.dependencies import get_current_user
from app.domain.growth.repository import QuestRepository
from app.domain.interview.models import User
from app.infrastructure.database import get_db

router = APIRouter(prefix="/quests", tags=["quests"])

VALID_STATUSES = {"generated", "in_progress", "submitted", "verified_pass", "verified_fail"}


@router.get("", response_model=QuestListResponse)
async def list_quests(
    status: str | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")

    repo = QuestRepository(db)
    quests = await repo.get_by_user(user.id, status_filter=status)
    return QuestListResponse(
        quests=[
            QuestResponse(
                id=str(q.id),
                quest_title=q.quest_title,
                quest_detail=q.quest_detail,
                status=q.status,
                verification_method=q.verification_method,
                target_skill_id=str(q.target_skill_id) if q.target_skill_id else None,
                due_date=q.due_date,
                created_at=q.created_at,
                completed_at=q.completed_at,
            )
            for q in quests
        ]
    )


@router.put("/{quest_id}/status", response_model=QuestResponse)
async def update_quest_status(
    quest_id: str,
    body: QuestStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {VALID_STATUSES}")

    repo = QuestRepository(db)
    quest = await repo.get_by_id(uuid.UUID(quest_id))
    if not quest or quest.user_id != user.id:
        raise HTTPException(status_code=404, detail="Quest not found")

    quest = await repo.update_status(uuid.UUID(quest_id), body.status)
    return QuestResponse(
        id=str(quest.id),
        quest_title=quest.quest_title,
        quest_detail=quest.quest_detail,
        status=quest.status,
        verification_method=quest.verification_method,
        target_skill_id=str(quest.target_skill_id) if quest.target_skill_id else None,
        due_date=quest.due_date,
        created_at=quest.created_at,
        completed_at=quest.completed_at,
    )
