"""Tests for resume endpoints."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


MOCK_LLM_RESPONSE = '{"basic_info": {"name": "Test User", "phone": "123", "email": "t@t.com", "education": []}, "skills": {"languages": ["Python"], "frameworks": [], "databases": [], "tools": []}, "projects": [], "work_experience": []}'


@pytest.mark.asyncio
@patch("app.api.v1.resumes.parse_file")
async def test_upload_resume(mock_parse_file, auth_client: AsyncClient):
    """Upload a resume returns immediately with parsing status."""
    mock_parse_file.return_value = "fake resume text content"

    pdf_content = b"%PDF-1.4 fake pdf content for testing"
    files = {"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
    data = {"title": "My Resume", "template_type": "backend"}

    resp = await auth_client.post("/api/resumes", files=files, data=data)
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "My Resume"
    assert body["template_type"] == "backend"
    assert body["parsing_status"] == "parsing"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.asyncio
@patch("app.api.v1.resumes.parse_file")
async def test_list_resumes(mock_parse_file, auth_client: AsyncClient):
    """List resumes returns uploaded resumes."""
    mock_parse_file.return_value = "text"

    files = {"file": ("r.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
    await auth_client.post("/api/resumes", files=files, data={"template_type": "generic"})

    resp = await auth_client.get("/api/resumes")
    assert resp.status_code == 200
    resumes = resp.json()["resumes"]
    assert len(resumes) >= 1


@pytest.mark.asyncio
@patch("app.api.v1.resumes.parse_file")
async def test_get_resume_by_id(mock_parse_file, auth_client: AsyncClient):
    mock_parse_file.return_value = "text"

    files = {"file": ("r.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
    create_resp = await auth_client.post("/api/resumes", files=files, data={"template_type": "generic"})
    resume_id = create_resp.json()["id"]

    resp = await auth_client.get(f"/api/resumes/{resume_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == resume_id


@pytest.mark.asyncio
async def test_get_resume_not_found(auth_client: AsyncClient):
    resp = await auth_client.get("/api/resumes/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.api.v1.resumes.parse_file")
async def test_delete_resume(mock_parse_file, auth_client: AsyncClient):
    mock_parse_file.return_value = "text"

    files = {"file": ("r.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
    create_resp = await auth_client.post("/api/resumes", files=files, data={"template_type": "generic"})
    resume_id = create_resp.json()["id"]

    resp = await auth_client.delete(f"/api/resumes/{resume_id}")
    assert resp.status_code == 204

    resp = await auth_client.get(f"/api/resumes/{resume_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.api.v1.resumes.parse_file")
async def test_set_default_resume(mock_parse_file, auth_client: AsyncClient):
    mock_parse_file.return_value = "text"

    files = {"file": ("r.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
    create_resp = await auth_client.post("/api/resumes", files=files, data={"template_type": "generic"})
    resume_id = create_resp.json()["id"]

    resp = await auth_client.post(f"/api/resumes/{resume_id}/set-default")
    assert resp.status_code == 200
    assert resp.json()["is_default"] is True


@pytest.mark.asyncio
@patch("app.api.v1.resumes.parse_file")
async def test_upload_resume_has_parsing_status(mock_parse_file, auth_client: AsyncClient):
    """Uploaded resume should have parsing_status field in response."""
    mock_parse_file.return_value = "text"

    files = {"file": ("r.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
    resp = await auth_client.post("/api/resumes", files=files, data={"template_type": "generic"})
    assert resp.status_code == 201
    body = resp.json()
    assert "parsing_status" in body
    assert body["parsing_status"] == "parsing"


@pytest.mark.asyncio
@patch("app.api.v1.resumes.parse_file")
async def test_list_resumes_includes_parsing_status(mock_parse_file, auth_client: AsyncClient):
    """Listed resumes include parsing_status field."""
    mock_parse_file.return_value = "text"

    files = {"file": ("r.pdf", io.BytesIO(b"%PDF"), "application/pdf")}
    await auth_client.post("/api/resumes", files=files, data={"template_type": "generic"})

    resp = await auth_client.get("/api/resumes")
    assert resp.status_code == 200
    for resume in resp.json()["resumes"]:
        assert "parsing_status" in resume
