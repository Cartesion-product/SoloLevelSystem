"""Tests for target job endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


MOCK_JD_PARSE_RESPONSE = '{"required_skills": ["Python", "FastAPI"], "preferred_skills": ["Docker"], "experience_years": "3-5", "key_responsibilities": ["Backend development"], "technical_domains": ["Web"]}'


@pytest.mark.asyncio
@patch("app.api.v1.jobs.get_llm_provider")
async def test_create_job(mock_get_llm, auth_client: AsyncClient):
    mock_llm = AsyncMock()
    mock_llm.chat = AsyncMock(return_value=MOCK_JD_PARSE_RESPONSE)
    mock_get_llm.return_value = mock_llm

    resp = await auth_client.post("/api/jobs", json={
        "company_name": "TestCorp",
        "position_name": "Backend Developer",
        "jd_text": "We need a Python developer with 3+ years experience...",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["position_name"] == "Backend Developer"
    assert body["company_name"] == "TestCorp"
    assert body["parsed_requirements"] is not None
    assert "Python" in body["parsed_requirements"]["required_skills"]


@pytest.mark.asyncio
@patch("app.api.v1.jobs.get_llm_provider")
async def test_list_jobs(mock_get_llm, auth_client: AsyncClient):
    mock_llm = AsyncMock()
    mock_llm.chat = AsyncMock(return_value=MOCK_JD_PARSE_RESPONSE)
    mock_get_llm.return_value = mock_llm

    await auth_client.post("/api/jobs", json={
        "position_name": "Job1",
        "jd_text": "desc",
    })
    await auth_client.post("/api/jobs", json={
        "position_name": "Job2",
        "jd_text": "desc2",
    })

    resp = await auth_client.get("/api/jobs")
    assert resp.status_code == 200
    assert len(resp.json()["jobs"]) == 2


@pytest.mark.asyncio
@patch("app.api.v1.jobs.get_llm_provider")
async def test_set_default_job(mock_get_llm, auth_client: AsyncClient):
    mock_llm = AsyncMock()
    mock_llm.chat = AsyncMock(return_value=MOCK_JD_PARSE_RESPONSE)
    mock_get_llm.return_value = mock_llm

    create_resp = await auth_client.post("/api/jobs", json={
        "position_name": "Dev",
        "jd_text": "desc",
    })
    job_id = create_resp.json()["id"]

    resp = await auth_client.post(f"/api/jobs/{job_id}/set-default")
    assert resp.status_code == 200
    assert resp.json()["is_default"] is True


@pytest.mark.asyncio
async def test_set_default_job_not_found(auth_client: AsyncClient):
    resp = await auth_client.post("/api/jobs/00000000-0000-0000-0000-000000000000/set-default")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_job_missing_fields(auth_client: AsyncClient):
    resp = await auth_client.post("/api/jobs", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
@patch("app.api.v1.jobs.get_llm_provider")
async def test_get_job_by_id(mock_get_llm, auth_client: AsyncClient):
    mock_llm = AsyncMock()
    mock_llm.chat = AsyncMock(return_value=MOCK_JD_PARSE_RESPONSE)
    mock_get_llm.return_value = mock_llm

    create_resp = await auth_client.post("/api/jobs", json={
        "company_name": "TestCorp",
        "position_name": "Backend Developer",
        "jd_text": "Python developer with 3+ years experience",
    })
    job_id = create_resp.json()["id"]

    resp = await auth_client.get(f"/api/jobs/{job_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == job_id
    assert body["position_name"] == "Backend Developer"
    assert body["company_name"] == "TestCorp"
    assert body["parsed_requirements"] is not None


@pytest.mark.asyncio
async def test_get_job_not_found(auth_client: AsyncClient):
    resp = await auth_client.get("/api/jobs/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.api.v1.jobs.get_llm_provider")
async def test_update_job(mock_get_llm, auth_client: AsyncClient):
    mock_llm = AsyncMock()
    mock_llm.chat = AsyncMock(return_value=MOCK_JD_PARSE_RESPONSE)
    mock_get_llm.return_value = mock_llm

    create_resp = await auth_client.post("/api/jobs", json={
        "company_name": "OldCorp",
        "position_name": "Dev",
        "jd_text": "desc",
    })
    job_id = create_resp.json()["id"]

    resp = await auth_client.put(f"/api/jobs/{job_id}", json={
        "company_name": "NewCorp",
        "position_name": "Senior Dev",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["company_name"] == "NewCorp"
    assert body["position_name"] == "Senior Dev"


@pytest.mark.asyncio
@patch("app.api.v1.jobs.get_llm_provider")
async def test_delete_job(mock_get_llm, auth_client: AsyncClient):
    mock_llm = AsyncMock()
    mock_llm.chat = AsyncMock(return_value=MOCK_JD_PARSE_RESPONSE)
    mock_get_llm.return_value = mock_llm

    create_resp = await auth_client.post("/api/jobs", json={
        "position_name": "ToDelete",
        "jd_text": "desc",
    })
    job_id = create_resp.json()["id"]

    resp = await auth_client.delete(f"/api/jobs/{job_id}")
    assert resp.status_code == 204

    list_resp = await auth_client.get("/api/jobs")
    job_ids = [j["id"] for j in list_resp.json()["jobs"]]
    assert job_id not in job_ids


@pytest.mark.asyncio
async def test_jobs_require_auth(client: AsyncClient):
    resp = await client.get("/api/jobs")
    assert resp.status_code == 403
