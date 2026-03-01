"""Node: execute_round — Generate the current round's interview question.

LLM call at medium temperature (0.7) to produce natural questions.
After outputting the question, the graph terminates and waits for user input.
"""

import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.v2.state import SessionState
from app.infrastructure.llm_provider import get_chat_model


async def execute_round_node(state: SessionState) -> dict:
    """Generate an interview question for the current round."""
    llm = get_chat_model(temperature=0.7)

    current_round = state.get("current_round", 0) + 1
    plan = state.get("plan", {})
    round_plan_list = plan.get("round_plan", [])
    system_prompt = state.get("system_prompt", "")
    mode = state.get("mode", "technical")

    # Determine this round's focus
    round_info = {}
    if round_plan_list and current_round <= len(round_plan_list):
        round_info = round_plan_list[current_round - 1]

    topic = round_info.get("topic", "general")
    difficulty = round_info.get("difficulty", "medium")
    goal = round_info.get("goal", "assess understanding")

    # Build conversation context (last 6 messages)
    recent_messages = []
    for m in state.get("messages", [])[-6:]:
        if isinstance(m, AIMessage):
            recent_messages.append({"role": "assistant", "content": m.content})
        elif isinstance(m, HumanMessage):
            recent_messages.append({"role": "user", "content": m.content})

    round_directive = f"""Round {current_round}/{state.get('max_rounds', 5)}
Topic: {topic}
Difficulty: {difficulty}
Goal: {goal}
Mode: {mode}

Generate ONE focused interview question for this round.
If there is prior conversation, build on it naturally.
Respond in Chinese."""

    messages = [
        SystemMessage(content=system_prompt + "\n\n" + round_directive),
    ]

    # Add conversation history
    for m in recent_messages:
        if m["role"] == "assistant":
            messages.append(AIMessage(content=m["content"]))
        else:
            messages.append(HumanMessage(content=m["content"]))

    response = await llm.ainvoke(messages)

    round_data = {
        "round": current_round,
        "topic": topic,
        "difficulty": difficulty,
        "question": response.content,
    }

    return {
        "current_round": current_round,
        "rounds": [round_data],
        "messages": [AIMessage(content=response.content)],
    }
