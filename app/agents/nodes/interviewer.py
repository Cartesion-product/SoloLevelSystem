"""Interviewer node: generates interview questions (the "mouth")."""

import json

from langchain_core.messages import AIMessage

from app.agents.prompts.interviewer import (
    INTERVIEWER_FEEDBACK_PROMPT,
    INTERVIEWER_ICEBREAK_PROMPT,
    INTERVIEWER_SYSTEM_PROMPT,
)
from app.agents.state import InterviewState
from app.infrastructure.llm_provider import get_llm_provider


async def interviewer_node(state: InterviewState) -> dict:
    """Generate the next interview question or response."""
    llm = get_llm_provider()
    action = state.get("next_action", "ask_question")

    if action == "end" or state.get("phase") == "feedback":
        return await _generate_feedback(state, llm)

    if action == "icebreak":
        return await _generate_icebreak(state, llm)

    return await _generate_question(state, llm)


async def _generate_question(state: InterviewState, llm) -> dict:
    """Generate a regular interview question."""
    system_prompt = INTERVIEWER_SYSTEM_PROMPT.format(
        interviewer_directive=state.get("interviewer_directive", "Ask the next question."),
    )

    # Build conversation history for LLM
    history = []
    for m in state.get("messages", [])[-10:]:
        role = "assistant" if isinstance(m, AIMessage) else "user"
        history.append({"role": role, "content": m.content})

    messages = [{"role": "system", "content": system_prompt}] + history

    response = await llm.chat(messages, temperature=0.7)

    return {
        "messages": [AIMessage(content=response)],
        "question_count": state.get("question_count", 0) + 1,
        "silence_count": 0,
    }


async def _generate_icebreak(state: InterviewState, llm) -> dict:
    """Generate an icebreaker when user is stuck."""
    silence = state.get("silence_count", 0)
    level = min(silence - 1, 3)

    prompt = INTERVIEWER_ICEBREAK_PROMPT.format(
        silence_count=silence,
        icebreak_level=level,
        topic=state.get("current_topic", "this topic"),
    )

    response = await llm.chat(
        [{"role": "system", "content": prompt}],
        temperature=0.7,
    )

    return {
        "messages": [AIMessage(content=response)],
    }


async def _generate_feedback(state: InterviewState, llm) -> dict:
    """Generate final interview feedback."""
    gaps = state.get("identified_gaps", [])
    scores = state.get("evaluation_scores", [])

    avg_score = sum(s.get("score", 5) for s in scores) / max(len(scores), 1)
    strengths = []
    weaknesses = []
    for s in scores:
        strengths.extend(s.get("key_points_hit", []))
        weaknesses.extend(s.get("key_points_missed", []))

    prompt = INTERVIEWER_FEEDBACK_PROMPT.format(
        question_count=state.get("question_count", 0),
        overall_assessment=f"Average score: {avg_score:.1f}/10",
        strengths=", ".join(set(strengths)[:10]) or "N/A",
        gaps=json.dumps(gaps, ensure_ascii=False)[:500],
    )

    response = await llm.chat(
        [{"role": "system", "content": prompt}],
        temperature=0.7,
    )

    summary = {
        "overall_score": round(avg_score, 1),
        "strengths": list(set(strengths)[:10]),
        "weaknesses": list(set(weaknesses)[:10]),
        "gap_list": [g.get("skill", g) if isinstance(g, dict) else str(g) for g in gaps],
        "question_count": state.get("question_count", 0),
    }

    return {
        "messages": [AIMessage(content=response)],
        "session_summary": json.dumps(summary, ensure_ascii=False),
        "phase": "feedback",
        "next_action": "end",
    }
