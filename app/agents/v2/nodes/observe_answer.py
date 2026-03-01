"""Node: observe_answer — Evaluate the user's answer for the current round.

LLM call at low temperature (0.1) for consistent scoring.
"""

import json

from langchain_core.messages import SystemMessage

from app.agents.v2.state import SessionState
from app.infrastructure.llm_provider import get_chat_model


async def observe_answer_node(state: SessionState) -> dict:
    """Evaluate the user's most recent answer against the round context."""
    llm = get_chat_model(temperature=0.1)

    eval_criteria = state.get("eval_criteria", "")
    rounds = state.get("rounds", [])
    messages = state.get("messages", [])

    # Get the last round info and user's answer
    current_round_data = rounds[-1] if rounds else {}
    question = current_round_data.get("question", "")
    topic = current_round_data.get("topic", "")
    difficulty = current_round_data.get("difficulty", "medium")

    # Extract latest user message
    user_answer = ""
    for m in reversed(messages):
        if hasattr(m, "type") and m.type == "human":
            user_answer = m.content
            break
        elif hasattr(m, "content") and not isinstance(m, type(messages[0])):
            # Fallback
            pass

    eval_prompt = f"""{eval_criteria}

---

Question asked: {question}
Topic: {topic}
Difficulty: {difficulty}

User's answer:
{user_answer}

Evaluate this answer. Output a JSON object:
{{
  "score": <float 0-10>,
  "key_points_hit": ["point1", "point2"],
  "key_points_missed": ["point1"],
  "gap_identified": "<skill gap or null>",
  "difficulty_suggestion": "increase" | "maintain" | "decrease",
  "feedback": "<constructive feedback in Chinese, 1-2 sentences>",
  "skill_updates": [
    {{"skill_name": "...", "score": <float>}}
  ]
}}

Return ONLY valid JSON."""

    response = await llm.ainvoke([
        SystemMessage(content=eval_prompt),
    ])

    # Parse evaluation
    evaluation = {}
    try:
        evaluation = json.loads(response.content)
    except (json.JSONDecodeError, TypeError, AttributeError):
        evaluation = {
            "score": 5.0,
            "key_points_hit": [],
            "key_points_missed": [],
            "gap_identified": None,
            "difficulty_suggestion": "maintain",
            "feedback": "评估解析失败，使用默认评分。",
            "skill_updates": [],
        }

    # Build workspace updates from evaluation
    workspace_updates = state.get("workspace_updates", {})
    skill_updates = workspace_updates.get("skill_updates", [])
    new_weak_points = workspace_updates.get("new_weak_points", [])

    # Accumulate skill updates
    for su in evaluation.get("skill_updates", []):
        skill_updates.append(su)

    # If a gap is identified, add as weak point
    gap = evaluation.get("gap_identified")
    if gap:
        new_weak_points.append({
            "skill_name": gap,
            "severity": "high" if evaluation.get("score", 5) < 3 else "medium",
            "identified_in_session": state.get("session_id", ""),
            "description": evaluation.get("feedback", ""),
        })

    return {
        "round_scores": [evaluation],
        "round_feedbacks": [evaluation.get("feedback", "")],
        "workspace_updates": {
            **workspace_updates,
            "skill_updates": skill_updates,
            "new_weak_points": new_weak_points,
        },
    }
