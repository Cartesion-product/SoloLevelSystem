"""Tests for domain services (LLM parsing, skill tree init, file parsing)."""

import json
from unittest.mock import AsyncMock

import pytest

from app.domain.interview.service import parse_jd_with_llm, parse_resume_with_llm
from app.infrastructure.file_parser import parse_file


# ---- File parser tests ----

class TestFileParser:
    def test_parse_txt(self):
        text = parse_file(b"hello world", "test.txt")
        assert text == "hello world"

    def test_parse_md(self):
        text = parse_file("# Title\ncontent".encode(), "readme.md")
        assert "Title" in text

    def test_unsupported_format(self):
        with pytest.raises(ValueError, match="Unsupported"):
            parse_file(b"data", "file.xyz")


# ---- Resume LLM parsing tests ----

class TestResumeParsingLLM:
    @pytest.mark.asyncio
    async def test_parse_resume_valid_json(self):
        expected = {
            "basic_info": {"name": "Alice", "phone": "123", "email": "a@b.com", "education": []},
            "skills": {"languages": ["Python"]},
            "projects": [],
            "work_experience": [],
        }
        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value=json.dumps(expected))

        result = await parse_resume_with_llm("some resume text", "generic", mock_llm)
        assert result["basic_info"]["name"] == "Alice"
        assert "Python" in result["skills"]["languages"]

    @pytest.mark.asyncio
    async def test_parse_resume_markdown_wrapped(self):
        """LLM returns JSON wrapped in ```json ... ``` code block."""
        inner = '{"basic_info": {"name": "Bob"}, "skills": {}, "projects": [], "work_experience": []}'
        wrapped = f"```json\n{inner}\n```"
        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value=wrapped)

        result = await parse_resume_with_llm("text", "backend", mock_llm)
        assert result["basic_info"]["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_parse_resume_invalid_json_raises(self):
        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value="not valid json at all")

        with pytest.raises(json.JSONDecodeError):
            await parse_resume_with_llm("text", "generic", mock_llm)

    @pytest.mark.asyncio
    async def test_parse_resume_uses_correct_template(self):
        """Verify the prompt includes the correct template focus."""
        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value='{"basic_info": {}, "skills": {}, "projects": [], "work_experience": []}')

        await parse_resume_with_llm("text", "ai_dev", mock_llm)

        call_args = mock_llm.chat.call_args[0][0]  # first positional arg = messages
        prompt = call_args[0]["content"]
        assert "ai_dev" in prompt
        assert "AI frameworks" in prompt


# ---- JD parsing tests ----

class TestJDParsingLLM:
    @pytest.mark.asyncio
    async def test_parse_jd_valid_json(self):
        expected = {
            "required_skills": ["Python"],
            "preferred_skills": [],
            "experience_years": "3",
            "key_responsibilities": ["dev"],
            "technical_domains": ["backend"],
        }
        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value=json.dumps(expected))

        result = await parse_jd_with_llm("Job desc", mock_llm)
        assert "Python" in result["required_skills"]

    @pytest.mark.asyncio
    async def test_parse_jd_invalid_json_raises(self):
        mock_llm = AsyncMock()
        mock_llm.chat = AsyncMock(return_value="invalid")

        with pytest.raises(json.JSONDecodeError):
            await parse_jd_with_llm("desc", mock_llm)
