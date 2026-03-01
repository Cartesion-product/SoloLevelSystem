"""Tests for Workspace repository and service (using mongomock-motor)."""

import pytest
import pytest_asyncio

from app.domain.workspace.models import (
    SessionRecord,
    SkillRadar,
    SkillRadarEntry,
    TrainingPlan,
    UserMeta,
    WeakPoint,
)
from app.domain.workspace.repository import WorkspaceRepository


@pytest_asyncio.fixture
async def mongo_db():
    """Provide a mock MongoDB database using mongomock-motor."""
    from mongomock_motor import AsyncMongoMockClient
    client = AsyncMongoMockClient()
    db = client["test_solo_leveling"]
    yield db
    client.close()


@pytest_asyncio.fixture
async def repo(mongo_db) -> WorkspaceRepository:
    return WorkspaceRepository(mongo_db)


TEST_USER_ID = "00000000-0000-0000-0000-000000000001"


class TestProfileCRUD:
    @pytest.mark.asyncio
    async def test_create_and_get_profile(self, repo: WorkspaceRepository):
        profile = UserMeta(user_id=TEST_USER_ID, display_name="Test User")
        await repo.upsert_profile(profile)

        loaded = await repo.get_profile(TEST_USER_ID)
        assert loaded is not None
        assert loaded.user_id == TEST_USER_ID
        assert loaded.display_name == "Test User"

    @pytest.mark.asyncio
    async def test_upsert_updates_existing(self, repo: WorkspaceRepository):
        await repo.upsert_profile(UserMeta(user_id=TEST_USER_ID, display_name="V1"))
        await repo.upsert_profile(UserMeta(user_id=TEST_USER_ID, display_name="V2"))

        loaded = await repo.get_profile(TEST_USER_ID)
        assert loaded.display_name == "V2"

    @pytest.mark.asyncio
    async def test_get_nonexistent_profile(self, repo: WorkspaceRepository):
        result = await repo.get_profile("nonexistent")
        assert result is None


class TestSkillRadarCRUD:
    @pytest.mark.asyncio
    async def test_create_and_get_radar(self, repo: WorkspaceRepository):
        radar = SkillRadar(entries=[
            SkillRadarEntry(skill_name="Python", score=8.5),
            SkillRadarEntry(skill_name="SQL", score=6.0),
        ])
        await repo.upsert_skill_radar(TEST_USER_ID, radar)

        loaded = await repo.get_skill_radar(TEST_USER_ID)
        assert loaded is not None
        assert len(loaded.entries) == 2
        assert loaded.entries[0].skill_name == "Python"
        assert loaded.entries[0].score == 8.5

    @pytest.mark.asyncio
    async def test_get_nonexistent_radar(self, repo: WorkspaceRepository):
        result = await repo.get_skill_radar("nonexistent")
        assert result is None


class TestWeakPointsCRUD:
    @pytest.mark.asyncio
    async def test_add_and_get_weak_points(self, repo: WorkspaceRepository):
        wp = WeakPoint(skill_name="System Design", severity="high", description="Needs practice")
        await repo.add_weak_point(TEST_USER_ID, wp)

        points = await repo.get_weak_points(TEST_USER_ID)
        assert len(points) == 1
        assert points[0].skill_name == "System Design"
        assert points[0].severity == "high"

    @pytest.mark.asyncio
    async def test_resolved_points_filtered(self, repo: WorkspaceRepository):
        await repo.add_weak_point(TEST_USER_ID, WeakPoint(skill_name="A", resolved=False))
        await repo.add_weak_point(TEST_USER_ID, WeakPoint(skill_name="B", resolved=True))

        unresolved = await repo.get_weak_points(TEST_USER_ID, include_resolved=False)
        assert len(unresolved) == 1
        assert unresolved[0].skill_name == "A"

        all_points = await repo.get_weak_points(TEST_USER_ID, include_resolved=True)
        assert len(all_points) == 2

    @pytest.mark.asyncio
    async def test_resolve_weak_point(self, repo: WorkspaceRepository):
        await repo.add_weak_point(TEST_USER_ID, WeakPoint(skill_name="X"))
        await repo.resolve_weak_point(TEST_USER_ID, "X")

        points = await repo.get_weak_points(TEST_USER_ID, include_resolved=False)
        assert len(points) == 0


class TestSessionRecordsCRUD:
    @pytest.mark.asyncio
    async def test_add_and_list_sessions(self, repo: WorkspaceRepository):
        record = SessionRecord(
            session_id="session-1",
            mode="technical",
            overall_score=7.5,
            round_count=5,
        )
        await repo.add_session_record(TEST_USER_ID, record)

        sessions = await repo.get_sessions(TEST_USER_ID)
        assert len(sessions) == 1
        assert sessions[0].session_id == "session-1"
        assert sessions[0].overall_score == 7.5


class TestTrainingPlanCRUD:
    @pytest.mark.asyncio
    async def test_save_and_get_latest_plan(self, repo: WorkspaceRepository):
        plan = TrainingPlan(
            plan_id="plan-1",
            mode="technical",
            target_topics=["Python", "SQL"],
            strategy_notes="Focus on weak areas",
        )
        await repo.save_plan(TEST_USER_ID, plan)

        latest = await repo.get_latest_plan(TEST_USER_ID)
        assert latest is not None
        assert latest.plan_id == "plan-1"
        assert "Python" in latest.target_topics

    @pytest.mark.asyncio
    async def test_get_plan_nonexistent(self, repo: WorkspaceRepository):
        result = await repo.get_latest_plan("nonexistent")
        assert result is None
