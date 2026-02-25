"""Growth domain repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.growth.models import MoodLog, QuestLog, UserPsychologyProfile


class QuestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        status_filter: str | None = None,
    ) -> list[QuestLog]:
        query = select(QuestLog).where(QuestLog.user_id == user_id)
        if status_filter:
            query = query.where(QuestLog.status == status_filter)
        query = query.order_by(QuestLog.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, quest_id: uuid.UUID) -> QuestLog | None:
        result = await self.db.execute(select(QuestLog).where(QuestLog.id == quest_id))
        return result.scalar_one_or_none()

    async def update_status(self, quest_id: uuid.UUID, new_status: str) -> QuestLog | None:
        quest = await self.get_by_id(quest_id)
        if not quest:
            return None
        quest.status = new_status
        await self.db.flush()
        await self.db.refresh(quest)
        return quest


class PsychologyProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: uuid.UUID) -> UserPsychologyProfile | None:
        result = await self.db.execute(
            select(UserPsychologyProfile).where(UserPsychologyProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
