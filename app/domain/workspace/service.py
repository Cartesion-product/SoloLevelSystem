"""Workspace service — orchestrates workspace operations."""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.workspace.models import (
    SessionRecord,
    SkillRadar,
    SkillRadarEntry,
    TrainingPlan,
    UserMeta,
    WeakPoint,
)
from app.domain.workspace.repository import WorkspaceRepository


class WorkspaceManager:
    """High-level operations on user workspaces."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = WorkspaceRepository(db)

    async def load_for_session(self, user_id: str) -> dict:
        """Load workspace state needed by v2 graph nodes.

        Returns a dict ready to merge into SessionState.
        """
        profile = await self.repo.get_profile(user_id)
        radar = await self.repo.get_skill_radar(user_id)
        weak_points = await self.repo.get_weak_points(user_id)
        plan = await self.repo.get_latest_plan(user_id)

        return {
            "user_profile": profile.model_dump() if profile else {},
            "skill_radar": [e.model_dump() for e in radar.entries] if radar else [],
            "weak_points": [w.model_dump() for w in weak_points],
            "training_plan": plan.model_dump() if plan else {},
        }

    async def initialize_from_v1(self, user_id: str, pg_session: AsyncSession) -> None:
        """Migrate data from PostgreSQL (v1) to MongoDB workspace on first v2 use.

        Reads skill_tree from PG and creates corresponding workspace entries.
        """
        from sqlalchemy import select
        from app.domain.capability.models import SkillTree

        # Check if workspace already exists
        existing = await self.repo.get_profile(user_id)
        if existing:
            return  # Already initialized

        # Read PG skill tree
        result = await pg_session.execute(
            select(SkillTree).where(SkillTree.user_id == user_id)
        )
        skills = list(result.scalars().all())

        # Create skill radar entries
        entries = []
        weak_points = []
        for s in skills:
            entry = SkillRadarEntry(
                skill_name=s.skill_name,
                score=float(s.proficiency_score),
                source=s.source_type,
                last_assessed=s.last_assessed_at,
                assess_count=s.assess_count,
            )
            entries.append(entry)

            # Skills with low score are weak points
            if s.proficiency_score < 4 and s.source_type in ("verified", "gap_detected"):
                weak_points.append(WeakPoint(
                    skill_name=s.skill_name,
                    severity="high" if s.proficiency_score < 2 else "medium",
                    description=s.evaluation_comment or f"Low proficiency in {s.skill_name}",
                ))

        # Save to MongoDB
        profile = UserMeta(user_id=user_id)
        await self.repo.upsert_profile(profile)

        radar = SkillRadar(entries=entries)
        await self.repo.upsert_skill_radar(user_id, radar)

        for wp in weak_points:
            await self.repo.add_weak_point(user_id, wp)

    async def update_after_session(self, user_id: str, session_state: dict) -> None:
        """Write back session results to the workspace.

        Called by the update_workspace graph node.
        """
        workspace_updates = session_state.get("workspace_updates", {})

        # Update skill radar
        new_scores = workspace_updates.get("skill_updates", [])
        if new_scores:
            radar = await self.repo.get_skill_radar(user_id)
            if not radar:
                radar = SkillRadar()

            existing_map = {e.skill_name: e for e in radar.entries}
            for update in new_scores:
                name = update["skill_name"]
                if name in existing_map:
                    entry = existing_map[name]
                    # Weighted average
                    entry.assess_count += 1
                    entry.score = round(
                        (entry.score * (entry.assess_count - 1) + update["score"])
                        / entry.assess_count, 1
                    )
                    entry.source = "verified"
                    entry.last_assessed = datetime.now(timezone.utc)
                else:
                    radar.entries.append(SkillRadarEntry(
                        skill_name=name,
                        score=update["score"],
                        source="verified",
                        last_assessed=datetime.now(timezone.utc),
                        assess_count=1,
                    ))

            radar.updated_at = datetime.now(timezone.utc)
            await self.repo.upsert_skill_radar(user_id, radar)

        # Add new weak points
        new_weak = workspace_updates.get("new_weak_points", [])
        for wp_data in new_weak:
            wp = WeakPoint(**wp_data)
            await self.repo.add_weak_point(user_id, wp)

        # Save session record
        summary = session_state.get("session_summary", {})
        if isinstance(summary, str):
            import json
            try:
                summary = json.loads(summary)
            except (json.JSONDecodeError, TypeError):
                summary = {}

        record = SessionRecord(
            session_id=session_state.get("session_id", ""),
            mode=session_state.get("mode", "technical"),
            target_company=session_state.get("target_company"),
            overall_score=summary.get("overall_score", 0.0),
            round_count=session_state.get("current_round", 0),
            strengths=summary.get("strengths", []),
            weaknesses=summary.get("weaknesses", []),
        )
        await self.repo.add_session_record(user_id, record)

        # Update profile
        profile = await self.repo.get_profile(user_id)
        if profile:
            profile.total_sessions += 1
            profile.last_session_at = datetime.now(timezone.utc)
            await self.repo.upsert_profile(profile)

        # Save training plan if generated
        plan_data = workspace_updates.get("training_plan")
        if plan_data:
            plan = TrainingPlan(**plan_data)
            await self.repo.save_plan(user_id, plan)
