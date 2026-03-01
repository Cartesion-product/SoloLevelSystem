"""Sync MongoDB workspace data back to PostgreSQL for v1 Dashboard compatibility."""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.capability.models import SkillTree
from app.domain.workspace.repository import WorkspaceRepository


async def sync_workspace_to_pg(user_id: str, mongo_db: AsyncIOMotorDatabase, pg_session: AsyncSession) -> None:
    """One-way sync: MongoDB skill_radar -> PostgreSQL skill_tree.

    Ensures v1 Dashboard sees updated skill scores after v2 sessions.
    """
    repo = WorkspaceRepository(mongo_db)
    radar = await repo.get_skill_radar(user_id)
    if not radar:
        return

    import uuid as _uuid

    user_uuid = _uuid.UUID(user_id)

    for entry in radar.entries:
        result = await pg_session.execute(
            select(SkillTree).where(
                SkillTree.user_id == user_uuid,
                SkillTree.skill_name == entry.skill_name,
            )
        )
        skill = result.scalar_one_or_none()

        if skill:
            skill.proficiency_score = max(0, min(10, round(entry.score)))
            skill.assess_count = entry.assess_count
            skill.source_type = entry.source
            skill.last_assessed_at = entry.last_assessed or datetime.now(timezone.utc)
        else:
            # Create new skill in PG
            new_skill = SkillTree(
                user_id=user_uuid,
                skill_name=entry.skill_name,
                proficiency_score=max(0, min(10, round(entry.score))),
                source_type=entry.source,
                assess_count=entry.assess_count,
                last_assessed_at=entry.last_assessed,
            )
            pg_session.add(new_skill)

    await pg_session.flush()
