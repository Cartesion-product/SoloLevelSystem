"""PsychoAnalyst node: async emotional analysis and personality profiling."""

import json
from typing import Any

from app.infrastructure.llm_provider import BaseLLMProvider, get_llm_provider

PSYCHO_ANALYST_PROMPT = """You are a psychological analyst for an interview coaching system.
Analyze the interview conversation and provide:

1. **Detected mood**: The dominant emotion (anxious, confident, confused, giving_up, neutral, motivated)
2. **Personality tags**: Update tags based on behavior patterns (e.g., visual_learner, defensive_under_pressure, detail_oriented, big_picture_thinker)
3. **Confidence adjustment**: Suggest +/- delta to confidence_score (range -0.2 to +0.2)
4. **Resilience adjustment**: Suggest +/- delta to resilience_score
5. **Daily motivation**: Generate a personalized motivational message in Chinese

Output JSON:
{{
  "detected_mood": "<mood>",
  "personality_tags": ["tag1", "tag2"],
  "confidence_delta": <float>,
  "resilience_delta": <float>,
  "daily_motivation": "<motivational message in Chinese>",
  "trigger_event": "<what triggered the mood>"
}}

Return ONLY valid JSON."""


async def analyze_psychology(
    conversation_messages: list[dict],
    current_profile: dict[str, Any],
    llm: BaseLLMProvider | None = None,
) -> dict[str, Any]:
    """Analyze interview conversation for emotional patterns."""
    if llm is None:
        llm = get_llm_provider()

    # Build conversation summary
    conv_text = "\n".join(
        f"{'User' if m.get('type') == 'human' else 'Interviewer'}: {m.get('content', '')[:200]}"
        for m in conversation_messages[-20:]
    )

    prompt = f"""{PSYCHO_ANALYST_PROMPT}

Current profile:
- Confidence: {current_profile.get('confidence_score', 0.5)}
- Resilience: {current_profile.get('resilience_score', 0.5)}
- Existing tags: {json.dumps(current_profile.get('personality_tags', []))}

Conversation:
{conv_text}"""

    response = await llm.chat([{"role": "user", "content": prompt}], temperature=0.3)

    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "detected_mood": "neutral",
            "personality_tags": current_profile.get("personality_tags", []),
            "confidence_delta": 0.0,
            "resilience_delta": 0.0,
            "daily_motivation": "每一次练习都让你离目标更近一步。",
            "trigger_event": "analysis_failed",
        }
