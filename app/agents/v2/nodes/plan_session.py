"""Node: plan_session — Generate a training plan based on workspace state.

LLM call at low temperature (0.3) to produce a structured plan.
"""

import json
import uuid

from langchain_core.messages import AIMessage, SystemMessage

from app.agents.v2.state import SessionState
from app.infrastructure.llm_provider import get_chat_model


async def plan_session_node(state: SessionState) -> dict:
    """Analyze skill_radar and weak_points to create a focused training plan."""
    llm = get_chat_model(temperature=0.3)

    mode = state.get("mode", "technical")
    weak_points = state.get("weak_points", [])
    skill_radar = state.get("skill_radar", [])
    max_rounds = state.get("max_rounds", 5)

    # Build context for the planner
    weak_summary = ", ".join(
        wp.get("skill_name", "unknown") for wp in weak_points[:10]
    ) or "none identified yet"

    low_skills = [
        s for s in skill_radar if s.get("score", 10) < 5
    ]
    low_summary = ", ".join(
        f"{s['skill_name']}({s['score']})" for s in low_skills[:10]
    ) or "all skills above threshold"

    planning_prompt = f"""You are an interview training planner. Based on the candidate's profile, create a focused training plan.

Mode: {mode}
Max rounds: {max_rounds}
Known weak points: {weak_summary}
Low-scoring skills: {low_summary}

Output a JSON object:
{{
  "target_topics": ["topic1", "topic2", ...],
  "focus_weak_points": ["skill1", "skill2", ...],
  "strategy_notes": "<brief strategy for this session>",
  "round_plan": [
    {{"round": 1, "topic": "...", "difficulty": "easy|medium|hard", "goal": "..."}},
    ...
  ]
}}

Return ONLY valid JSON."""

    response = await llm.ainvoke([
        SystemMessage(content=planning_prompt),
    ])

    # Parse plan
    plan = {}
    try:
        plan = json.loads(response.content)
    except (json.JSONDecodeError, TypeError, AttributeError):
        plan = {
            "target_topics": [wp.get("skill_name", "general") for wp in weak_points[:max_rounds]],
            "focus_weak_points": [wp.get("skill_name", "") for wp in weak_points[:3]],
            "strategy_notes": "Fallback plan: cover weak points sequentially.",
            "round_plan": [
                {"round": i + 1, "topic": wp.get("skill_name", "general"), "difficulty": "medium", "goal": "assess"}
                for i, wp in enumerate(weak_points[:max_rounds])
            ],
        }

    plan["plan_id"] = str(uuid.uuid4())
    plan["mode"] = mode

    return {
        "plan": plan,
        "current_round": 0,
        "messages": [AIMessage(content=plan.get("strategy_notes", "Training plan created."))],
    }
