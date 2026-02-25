"""Capability domain repository."""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.capability.models import SkillAdvice, SkillTree


class SkillTreeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID, **kwargs) -> SkillTree:
        skill = SkillTree(user_id=user_id, **kwargs)
        self.db.add(skill)
        await self.db.flush()
        await self.db.refresh(skill)
        return skill

    async def get_by_user(self, user_id: uuid.UUID) -> list[SkillTree]:
        result = await self.db.execute(
            select(SkillTree).where(SkillTree.user_id == user_id).order_by(SkillTree.skill_name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, skill_id: uuid.UUID) -> SkillTree | None:
        result = await self.db.execute(select(SkillTree).where(SkillTree.id == skill_id))
        return result.scalar_one_or_none()

    async def find_by_name(self, user_id: uuid.UUID, skill_name: str) -> SkillTree | None:
        result = await self.db.execute(
            select(SkillTree).where(SkillTree.user_id == user_id, SkillTree.skill_name == skill_name)
        )
        return result.scalar_one_or_none()

    async def update(self, skill_id: uuid.UUID, **kwargs) -> SkillTree | None:
        skill = await self.get_by_id(skill_id)
        if not skill:
            return None
        for key, value in kwargs.items():
            setattr(skill, key, value)
        await self.db.flush()
        await self.db.refresh(skill)
        return skill

    async def bulk_create(self, user_id: uuid.UUID, skills: list[dict]) -> list[SkillTree]:
        created = []
        for s in skills:
            skill = SkillTree(user_id=user_id, **s)
            self.db.add(skill)
            created.append(skill)
        await self.db.flush()
        for sk in created:
            await self.db.refresh(sk)
        return created

    async def delete_by_user(self, user_id: uuid.UUID) -> int:
        """Delete all skill tree nodes for a user. Returns number of rows deleted."""
        # Delete children first (those with parent_skill_id), then parents
        result = await self.db.execute(
            delete(SkillTree).where(
                SkillTree.user_id == user_id,
                SkillTree.parent_skill_id.isnot(None),
            )
        )
        child_count = result.rowcount
        result = await self.db.execute(
            delete(SkillTree).where(SkillTree.user_id == user_id)
        )
        await self.db.flush()
        return child_count + result.rowcount


class SkillAdviceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: uuid.UUID) -> SkillAdvice | None:
        result = await self.db.execute(
            select(SkillAdvice).where(SkillAdvice.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: uuid.UUID, strength_advice: str, weakness_advice: str) -> SkillAdvice:
        existing = await self.get_by_user(user_id)
        if existing:
            existing.strength_advice = strength_advice
            existing.weakness_advice = weakness_advice
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        advice = SkillAdvice(user_id=user_id, strength_advice=strength_advice, weakness_advice=weakness_advice)
        self.db.add(advice)
        await self.db.flush()
        await self.db.refresh(advice)
        return advice
