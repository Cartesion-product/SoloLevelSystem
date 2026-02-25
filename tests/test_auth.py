"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    payload = {"username": "dup", "email": "dup@example.com", "password": "secret123"}
    await client.post("/api/auth/register", json=payload)
    resp = await client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "username": "short",
        "email": "short@example.com",
        "password": "12345",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "username": "bademail",
        "email": "not-an-email",
        "password": "secret123",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "secret123",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "wrongpw",
        "email": "wrongpw@example.com",
        "password": "secret123",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "wrongpw@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/api/auth/login", json={
        "email": "nobody@example.com",
        "password": "secret123",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_settings(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "username": "settingsuser",
        "email": "settings@example.com",
        "password": "secret123",
    })
    login_resp = await client.post("/api/auth/login", json={
        "email": "settings@example.com",
        "password": "secret123",
    })
    token = login_resp.json()["access_token"]

    resp = await client.put(
        "/api/users/settings",
        json={"auto_update_knowledge": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["settings"]["auto_update_knowledge"] is True


@pytest.mark.asyncio
async def test_protected_endpoint_no_token(client: AsyncClient):
    resp = await client.put("/api/users/settings", json={"auto_update_knowledge": True})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_protected_endpoint_bad_token(client: AsyncClient):
    resp = await client.put(
        "/api/users/settings",
        json={"auto_update_knowledge": True},
        headers={"Authorization": "Bearer invalid_token_here"},
    )
    assert resp.status_code == 401
