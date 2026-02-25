"""Tests for quest endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.growth.models import QuestLog


@pytest.mark.asyncio
async def test_list_quests_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/api/quests")
    assert resp.status_code == 200
    assert resp.json()["quests"] == []


@pytest.mark.asyncio
async def test_list_quests_with_data(auth_client: AsyncClient, db_session: AsyncSession):
    user_resp = await auth_client.put("/api/users/settings", json={})
    user_id = user_resp.json()["id"]

    quest = QuestLog(
        user_id=user_id,
        quest_title="Learn Redis",
        quest_detail="Study Redis data structures and caching patterns",
        status="generated",
        verification_method="verbal_quiz",
    )
    db_session.add(quest)
    await db_session.commit()

    resp = await auth_client.get("/api/quests")
    assert resp.status_code == 200
    quests = resp.json()["quests"]
    assert len(quests) == 1
    assert quests[0]["quest_title"] == "Learn Redis"


@pytest.mark.asyncio
async def test_list_quests_filter_by_status(auth_client: AsyncClient, db_session: AsyncSession):
    user_resp = await auth_client.put("/api/users/settings", json={})
    user_id = user_resp.json()["id"]

    for s in ["generated", "in_progress", "generated"]:
        db_session.add(QuestLog(
            user_id=user_id,
            quest_title=f"Quest {s}",
            quest_detail="detail",
            status=s,
        ))
    await db_session.commit()

    resp = await auth_client.get("/api/quests", params={"status": "generated"})
    assert resp.status_code == 200
    assert len(resp.json()["quests"]) == 2

    resp = await auth_client.get("/api/quests", params={"status": "in_progress"})
    assert len(resp.json()["quests"]) == 1


@pytest.mark.asyncio
async def test_list_quests_invalid_status(auth_client: AsyncClient):
    resp = await auth_client.get("/api/quests", params={"status": "invalid"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_update_quest_status(auth_client: AsyncClient, db_session: AsyncSession):
    user_resp = await auth_client.put("/api/users/settings", json={})
    user_id = user_resp.json()["id"]

    quest = QuestLog(
        user_id=user_id,
        quest_title="Task",
        quest_detail="detail",
        status="generated",
    )
    db_session.add(quest)
    await db_session.commit()
    await db_session.refresh(quest)

    resp = await auth_client.put(f"/api/quests/{quest.id}/status", json={"status": "in_progress"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_update_quest_not_found(auth_client: AsyncClient):
    resp = await auth_client.put(
        "/api/quests/00000000-0000-0000-0000-000000000000/status",
        json={"status": "in_progress"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_quests_require_auth(client: AsyncClient):
    resp = await client.get("/api/quests")
    assert resp.status_code == 403
