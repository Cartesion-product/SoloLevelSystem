"""Three-layer Prompt Plugin Loader for v2 interview system.

Merges prompts from three layers:
  1. base/     — shared defaults
  2. modes/    — mode-specific (behavioral, technical, system_design, hr)
  3. targets/  — company-specific overrides

Later layers append to (or override same-key JSON fields of) earlier layers.
Template variables use {{variable}} syntax.
"""

import json
from pathlib import Path
from typing import Any

PLUGINS_DIR = Path(__file__).resolve().parent.parent.parent / "plugins"


class PromptPluginLoader:
    """Load and merge prompt plugins from the filesystem."""

    def __init__(self, plugins_dir: Path | None = None):
        self.plugins_dir = plugins_dir or PLUGINS_DIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_system_prompt(
        self,
        mode: str,
        target_company: str | None = None,
        variables: dict[str, str] | None = None,
    ) -> str:
        """Build a merged system prompt from base + mode + target layers.

        Args:
            mode: Interview mode (behavioral, technical, system_design, hr).
            target_company: Optional company name for target-layer override.
            variables: Template variables to substitute ({{key}} → value).

        Returns:
            Merged prompt string.
        """
        parts: list[str] = []

        # Layer 1: base interviewer persona
        base = self._read_md("base", "interviewer_persona.md")
        if base:
            parts.append(base)

        # Layer 2: mode system prompt
        mode_prompt = self._read_md(f"modes/{mode}", "system_prompt.md")
        if mode_prompt:
            parts.append(mode_prompt)

        # Layer 3: target company prompt
        if target_company:
            target_prompt = self._read_md(f"targets/{target_company}", "system_prompt.md")
            if target_prompt:
                parts.append(target_prompt)

        merged = "\n\n---\n\n".join(parts) if parts else ""

        if variables:
            merged = self._substitute(merged, variables)

        return merged

    def load_eval_criteria(
        self,
        mode: str,
        variables: dict[str, str] | None = None,
    ) -> str:
        """Load evaluation criteria: base scoring rubric + mode criteria.

        Args:
            mode: Interview mode.
            variables: Template variables.

        Returns:
            Merged evaluation criteria string.
        """
        parts: list[str] = []

        base = self._read_md("base", "scoring_rubric.md")
        if base:
            parts.append(base)

        mode_criteria = self._read_md(f"modes/{mode}", "eval_criteria.md")
        if mode_criteria:
            parts.append(mode_criteria)

        merged = "\n\n---\n\n".join(parts) if parts else ""

        if variables:
            merged = self._substitute(merged, variables)

        return merged

    def load_feedback_format(
        self,
        variables: dict[str, str] | None = None,
    ) -> str:
        """Load the feedback format template from base layer."""
        text = self._read_md("base", "feedback_format.md") or ""
        if variables:
            text = self._substitute(text, variables)
        return text

    def load_question_bank(self, mode: str) -> dict[str, Any]:
        """Load question bank JSON for a mode.

        Returns:
            Parsed JSON dict, or empty dict if not found.
        """
        return self._read_json(f"modes/{mode}", "question_bank.json")

    def load_scenarios(self, mode: str) -> dict[str, Any]:
        """Load scenarios JSON (system_design mode)."""
        return self._read_json(f"modes/{mode}", "scenarios.json")

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _read_md(self, subdir: str, filename: str) -> str | None:
        path = self.plugins_dir / subdir / filename
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
        return None

    def _read_json(self, subdir: str, filename: str) -> dict[str, Any]:
        path = self.plugins_dir / subdir / filename
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
        return {}

    @staticmethod
    def _substitute(text: str, variables: dict[str, str]) -> str:
        """Replace {{key}} placeholders with values."""
        for key, value in variables.items():
            text = text.replace("{{" + key + "}}", str(value))
        return text
