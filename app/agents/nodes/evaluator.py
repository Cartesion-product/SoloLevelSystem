"""Evaluator node: silently scores user answers."""

import json

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.prompts.evaluator import EVALUATOR_SYSTEM_PROMPT, EVALUATOR_USER_PROMPT
from app.agents.state import InterviewState
from app.infrastructure.llm_provider import get_llm_provider

SHORT_ANSWER_THRESHOLD = 30  # characters


async def evaluator_node(state: InterviewState) -> dict:
    """Evaluate the user's latest answer."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    # Find last user message and preceding AI question
    last_user_msg = None
    last_ai_msg = None
    for m in reversed(messages):
        if isinstance(m, HumanMessage) and last_user_msg is None:
            last_user_msg = m
        elif isinstance(m, AIMessage) and last_user_msg is not None:
            last_ai_msg = m
            break

    if not last_user_msg:
        return {}

    user_answer = last_user_msg.content
    question = last_ai_msg.content if last_ai_msg else ""

    # Check for short/empty answers → increment silence_count
    if len(user_answer.strip()) < SHORT_ANSWER_THRESHOLD:
        return {
            "silence_count": state.get("silence_count", 0) + 1,
            "current_evaluation": {"score": 0, "comment": "Answer too short"},
        }

    # LLM evaluation
    llm = get_llm_provider()

    user_prompt = EVALUATOR_USER_PROMPT.format(
        question=question[:500],
        current_topic=state.get("current_topic", ""),
        difficulty=state.get("difficulty", "medium"),
        expected_points="Based on the question context",
        user_answer=user_answer[:1000],
    )

    response = await llm.chat(
        [
            {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )

    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        evaluation = json.loads(text)
    except json.JSONDecodeError:
        evaluation = {"score": 5.0, "comment": "Could not parse evaluation"}

    # Update gaps
    gaps = list(state.get("identified_gaps", []))
    if evaluation.get("gap_identified"):
        gaps.append({
            "skill": evaluation["gap_identified"],
            "topic": state.get("current_topic", ""),
            "score": evaluation.get("score", 0),
        })

    # Update scores
    scores = list(state.get("evaluation_scores", []))
    scores.append(evaluation)

    # Adjust difficulty based on suggestion
    difficulty = state.get("difficulty", "medium")
    suggestion = evaluation.get("difficulty_suggestion", "maintain")
    difficulty_levels = ["easy", "medium", "hard", "expert"]
    idx = difficulty_levels.index(difficulty)
    if suggestion == "increase" and idx < 3:
        difficulty = difficulty_levels[idx + 1]
    elif suggestion == "decrease" and idx > 0:
        difficulty = difficulty_levels[idx - 1]

    return {
        "current_evaluation": evaluation,
        "identified_gaps": gaps,
        "evaluation_scores": scores,
        "difficulty": difficulty,
        "silence_count": 0,
    }
