"""Tests for the PromptPluginLoader three-layer merge system."""

import json
import tempfile
from pathlib import Path

import pytest

from app.agents.prompt_loader import PromptPluginLoader


@pytest.fixture
def tmp_plugins(tmp_path: Path) -> Path:
    """Create a temporary plugins directory for testing."""
    # Base layer
    base = tmp_path / "base"
    base.mkdir()
    (base / "interviewer_persona.md").write_text("Base persona: {{interviewer_directive}}", encoding="utf-8")
    (base / "scoring_rubric.md").write_text("Base rubric: score 0-10", encoding="utf-8")
    (base / "feedback_format.md").write_text("Feedback: {{question_count}} questions", encoding="utf-8")

    # Mode layer: technical
    tech = tmp_path / "modes" / "technical"
    tech.mkdir(parents=True)
    (tech / "system_prompt.md").write_text("Technical mode: focus on DS&A", encoding="utf-8")
    (tech / "eval_criteria.md").write_text("Technical criteria: correctness, depth", encoding="utf-8")
    (tech / "question_bank.json").write_text(
        json.dumps({"mode": "technical", "categories": [{"name": "ds", "questions": []}]}),
        encoding="utf-8",
    )

    # Mode layer: behavioral
    beh = tmp_path / "modes" / "behavioral"
    beh.mkdir(parents=True)
    (beh / "system_prompt.md").write_text("Behavioral mode: STAR method", encoding="utf-8")
    (beh / "eval_criteria.md").write_text("Behavioral criteria: STAR", encoding="utf-8")

    # Target layer: google
    google = tmp_path / "targets" / "google"
    google.mkdir(parents=True)
    (google / "system_prompt.md").write_text("Google specific: Googleyness matters", encoding="utf-8")

    return tmp_path


@pytest.fixture
def loader(tmp_plugins: Path) -> PromptPluginLoader:
    return PromptPluginLoader(plugins_dir=tmp_plugins)


class TestLoadSystemPrompt:
    def test_base_plus_mode(self, loader: PromptPluginLoader):
        result = loader.load_system_prompt("technical")
        assert "Base persona" in result
        assert "Technical mode" in result
        # Should be separated by ---
        assert "---" in result

    def test_all_three_layers(self, loader: PromptPluginLoader):
        result = loader.load_system_prompt("technical", target_company="google")
        assert "Base persona" in result
        assert "Technical mode" in result
        assert "Google specific" in result

    def test_unknown_mode_fallback(self, loader: PromptPluginLoader):
        """Unknown mode only returns base layer."""
        result = loader.load_system_prompt("nonexistent")
        assert "Base persona" in result
        assert "Technical mode" not in result

    def test_unknown_target_ignored(self, loader: PromptPluginLoader):
        result = loader.load_system_prompt("technical", target_company="unknown_company")
        assert "Base persona" in result
        assert "Technical mode" in result
        # No target-layer text
        assert "Google specific" not in result

    def test_variable_substitution(self, loader: PromptPluginLoader):
        result = loader.load_system_prompt(
            "technical",
            variables={"interviewer_directive": "Ask about Python"},
        )
        assert "Ask about Python" in result
        assert "{{interviewer_directive}}" not in result


class TestLoadEvalCriteria:
    def test_base_plus_mode(self, loader: PromptPluginLoader):
        result = loader.load_eval_criteria("technical")
        assert "Base rubric" in result
        assert "Technical criteria" in result

    def test_behavioral_criteria(self, loader: PromptPluginLoader):
        result = loader.load_eval_criteria("behavioral")
        assert "Base rubric" in result
        assert "STAR" in result


class TestLoadFeedbackFormat:
    def test_load_and_substitute(self, loader: PromptPluginLoader):
        result = loader.load_feedback_format(variables={"question_count": "5"})
        assert "5 questions" in result


class TestLoadQuestionBank:
    def test_load_json(self, loader: PromptPluginLoader):
        bank = loader.load_question_bank("technical")
        assert bank["mode"] == "technical"
        assert "categories" in bank

    def test_missing_bank_returns_empty(self, loader: PromptPluginLoader):
        bank = loader.load_question_bank("behavioral")
        assert bank == {}


class TestLoadScenarios:
    def test_missing_scenarios(self, loader: PromptPluginLoader):
        result = loader.load_scenarios("technical")
        assert result == {}
