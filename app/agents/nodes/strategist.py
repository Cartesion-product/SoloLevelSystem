"""Strategist node: decides next interview action (the "brain")."""

import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.prompts.strategist import STRATEGIST_SYSTEM_PROMPT, STRATEGIST_USER_PROMPT
from app.agents.state import InterviewState
from app.infrastructure.llm_provider import get_llm_provider


async def strategist_node(state: InterviewState) -> dict:
    """Analyze state and decide next interview action."""
    llm = get_llm_provider()

    # Extract recent messages for context (last 6 messages = 3 turns)
    recent = state.get("messages", [])[-6:]
    recent_text = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Interviewer'}: {m.content[:200]}"
        for m in recent
    )

    # Gather skill gaps
    skill_gaps = [
        s["skill_name"]
        for s in state.get("skill_tree_snapshot", [])
        if s.get("source_type") == "inferred_gap"
    ]

    # Resume skills summary
    resume_skills = []
    skills_data = state.get("resume_context", {}).get("skills", {})
    for category, items in skills_data.items():
        if isinstance(items, list):
            resume_skills.extend(items)

    # JD requirements
    jd_req = state.get("jd_context", {}).get("required_skills", [])

    user_prompt = STRATEGIST_USER_PROMPT.format(
        phase=state.get("phase", "defense"),
        question_count=state.get("question_count", 0),
        max_questions=state.get("max_questions", 8),
        difficulty=state.get("difficulty", "medium"),
        stress_level=state.get("stress_level", 0.3),
        silence_count=state.get("silence_count", 0),
        current_topic=state.get("current_topic", ""),
        gaps=json.dumps(state.get("identified_gaps", []), ensure_ascii=False)[:300],
        current_evaluation=json.dumps(state.get("current_evaluation", {}), ensure_ascii=False)[:300],
        resume_skills=", ".join(resume_skills[:15]),
        jd_requirements=", ".join(jd_req[:10]),
        skill_gaps=", ".join(skill_gaps[:10]),
        recent_messages=recent_text,
    )

    messages = [
        {"role": "system", "content": STRATEGIST_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    response = await llm.chat(messages, temperature=0.3)

    # Parse response
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        decision = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: continue asking
        decision = {
            "next_action": "ask_question",
            "phase": state.get("phase", "defense"),
            "difficulty": state.get("difficulty", "medium"),
            "stress_level": state.get("stress_level", 0.3),
            "current_topic": state.get("current_topic", ""),
            "interviewer_directive": "Continue with the next question on the current topic.",
        }

    # Force end if max questions reached
    if state.get("question_count", 0) >= state.get("max_questions", 8):
        decision["next_action"] = "end"
        decision["phase"] = "feedback"

    return {
        "next_action": decision.get("next_action", "ask_question"),
        "phase": decision.get("phase", state.get("phase", "defense")),
        "difficulty": decision.get("difficulty", state.get("difficulty", "medium")),
        "stress_level": decision.get("stress_level", state.get("stress_level", 0.3)),
        "current_topic": decision.get("current_topic", state.get("current_topic", "")),
        "interviewer_directive": decision.get("interviewer_directive", ""),
    }
