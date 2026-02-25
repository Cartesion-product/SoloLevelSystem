"""Tests for skill tree endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.capability.models import SkillTree
from app.domain.capability.repository import SkillTreeRepository
from app.domain.interview.models import User


@pytest.mark.asyncio
async def test_get_skill_tree_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/api/skills/tree")
    assert resp.status_code == 200
    assert resp.json()["skills"] == []


@pytest.mark.asyncio
async def test_get_skill_tree_with_data(auth_client: AsyncClient, db_session: AsyncSession):
    # Get user id from token
    resp = await auth_client.put("/api/users/settings", json={})
    user_id = resp.json()["id"]

    repo = SkillTreeRepository(db_session)
    await repo.create(
        user_id=user_id,
        skill_name="Python",
        proficiency_score=7,
        source_type="resume_claimed",
    )
    await repo.create(
        user_id=user_id,
        skill_name="FastAPI",
        proficiency_score=5,
        source_type="inferred_gap",
    )
    await db_session.commit()

    resp = await auth_client.get("/api/skills/tree")
    assert resp.status_code == 200
    skills = resp.json()["skills"]
    assert len(skills) == 2
    names = {s["skill_name"] for s in skills}
    assert names == {"Python", "FastAPI"}


@pytest.mark.asyncio
async def test_skills_require_auth(client: AsyncClient):
    resp = await client.get("/api/skills/tree")
    assert resp.status_code == 403
