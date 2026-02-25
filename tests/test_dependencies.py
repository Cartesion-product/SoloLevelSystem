"""Tests for auth dependencies (hash, verify, JWT)."""

import pytest

from app.dependencies import create_access_token, hash_password, verify_password


class TestPasswordHashing:
    def test_hash_and_verify(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert verify_password("mypassword", hashed)

    def test_verify_wrong_password(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses random salt

    def test_unicode_password(self):
        hashed = hash_password("密码测试123")
        assert verify_password("密码测试123", hashed)


class TestJWT:
    def test_create_token_returns_string(self):
        token = create_access_token("user-id-123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_decodable(self):
        from jose import jwt
        from app.config import get_settings

        settings = get_settings()
        token = create_access_token("user-abc")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == "user-abc"
        assert "exp" in payload
