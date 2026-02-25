"""QuestMaster node: generates learning tasks based on identified gaps."""

import json
from typing import Any

from app.infrastructure.llm_provider import BaseLLMProvider, get_llm_provider

QUEST_MASTER_PROMPT = """You are a learning quest generator for an interview coaching system.
Based on identified knowledge gaps from an interview session, generate specific, actionable learning tasks.

Each task should:
- Target a specific skill gap
- Be completable within 1-3 days
- Have a clear verification method (verbal_quiz, code_review, or concept_explain)
- Include detailed steps

Output JSON array:
[
  {{
    "quest_title": "<concise title>",
    "quest_detail": "<detailed description with specific steps>",
    "target_skill": "<skill name>",
    "verification_method": "verbal_quiz" | "code_review" | "concept_explain",
    "estimated_days": <int 1-3>
  }}
]

Generate 2-5 tasks. Return ONLY valid JSON array."""


async def generate_quests(
    identified_gaps: list[dict],
    skill_tree_snapshot: list[dict],
    llm: BaseLLMProvider | None = None,
) -> list[dict[str, Any]]:
    """Generate learning quests from interview gaps."""
    if llm is None:
        llm = get_llm_provider()

    if not identified_gaps:
        return []

    gaps_text = json.dumps(identified_gaps, ensure_ascii=False)
    skills_text = json.dumps(
        [{"name": s["skill_name"], "score": s["proficiency_score"]}
         for s in skill_tree_snapshot[:20]],
        ensure_ascii=False,
    )

    prompt = f"""{QUEST_MASTER_PROMPT}

Identified gaps from this session:
{gaps_text}

Current skill tree (top skills):
{skills_text}"""

    response = await llm.chat([{"role": "user", "content": prompt}], temperature=0.5)

    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        quests = json.loads(text)
        return quests if isinstance(quests, list) else []
    except json.JSONDecodeError:
        return []
