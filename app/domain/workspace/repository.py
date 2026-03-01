"""Workspace MongoDB repository."""

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.workspace.models import (
    SessionRecord,
    SkillRadar,
    SkillRadarEntry,
    TrainingPlan,
    UserMeta,
    WeakPoint,
)


class WorkspaceRepository:
    """CRUD operations for workspace data in MongoDB."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.profiles = db["workspace_profiles"]
        self.skill_radars = db["workspace_skill_radars"]
        self.weak_points = db["workspace_weak_points"]
        self.sessions = db["workspace_sessions"]
        self.plans = db["workspace_plans"]

    # --- Profile ---
    async def get_profile(self, user_id: str) -> UserMeta | None:
        doc = await self.profiles.find_one({"user_id": user_id})
        if doc:
            doc.pop("_id", None)
            return UserMeta(**doc)
        return None

    async def upsert_profile(self, profile: UserMeta) -> None:
        await self.profiles.update_one(
            {"user_id": profile.user_id},
            {"$set": profile.model_dump()},
            upsert=True,
        )

    # --- Skill Radar ---
    async def get_skill_radar(self, user_id: str) -> SkillRadar | None:
        doc = await self.skill_radars.find_one({"user_id": user_id})
        if doc:
            doc.pop("_id", None)
            doc.pop("user_id", None)
            return SkillRadar(**doc)
        return None

    async def upsert_skill_radar(self, user_id: str, radar: SkillRadar) -> None:
        data = radar.model_dump()
        data["user_id"] = user_id
        await self.skill_radars.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True,
        )

    # --- Weak Points ---
    async def get_weak_points(self, user_id: str, include_resolved: bool = False) -> list[WeakPoint]:
        query: dict = {"user_id": user_id}
        if not include_resolved:
            query["resolved"] = False
        cursor = self.weak_points.find(query)
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            doc.pop("user_id", None)
            results.append(WeakPoint(**doc))
        return results

    async def add_weak_point(self, user_id: str, wp: WeakPoint) -> None:
        data = wp.model_dump()
        data["user_id"] = user_id
        await self.weak_points.insert_one(data)

    async def resolve_weak_point(self, user_id: str, skill_name: str) -> None:
        await self.weak_points.update_many(
            {"user_id": user_id, "skill_name": skill_name},
            {"$set": {"resolved": True}},
        )

    # --- Session Records ---
    async def get_sessions(self, user_id: str, limit: int = 20) -> list[SessionRecord]:
        cursor = (
            self.sessions.find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            doc.pop("user_id", None)
            results.append(SessionRecord(**doc))
        return results

    async def add_session_record(self, user_id: str, record: SessionRecord) -> None:
        data = record.model_dump()
        data["user_id"] = user_id
        await self.sessions.insert_one(data)

    # --- Training Plans ---
    async def get_latest_plan(self, user_id: str) -> TrainingPlan | None:
        doc = await self.plans.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)],
        )
        if doc:
            doc.pop("_id", None)
            doc.pop("user_id", None)
            return TrainingPlan(**doc)
        return None

    async def save_plan(self, user_id: str, plan: TrainingPlan) -> None:
        data = plan.model_dump()
        data["user_id"] = user_id
        await self.plans.insert_one(data)
