"""v2 SessionState definition for the Plan-Execute-Observe LangGraph."""

import operator
from typing import Annotated, Any, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class SessionState(TypedDict):
    """State for the v2 Plan-Execute-Observe interview graph.

    Fields are grouped by concern. Annotated lists use operator.add
    so each node can *append* without overwriting previous entries.
    """

    # --- Identity ---
    user_id: str
    session_id: str

    # --- Workspace (loaded from MongoDB) ---
    user_profile: dict
    skill_radar: list[dict]
    weak_points: list[dict]

    # --- Configuration ---
    mode: str  # behavioral | technical | system_design | hr
    target_company: str | None
    system_prompt: str
    eval_criteria: str

    # --- Plan ---
    plan: dict  # Training plan from plan_session node

    # --- Execution ---
    rounds: Annotated[list[dict], operator.add]  # Each round: {question, answer, score, feedback}
    current_round: int
    max_rounds: int

    # --- Conversation (SSE compatible) ---
    messages: Annotated[list[BaseMessage], add_messages]

    # --- Evaluation ---
    round_scores: Annotated[list[dict], operator.add]
    round_feedbacks: Annotated[list[str], operator.add]

    # --- Output ---
    session_summary: dict
    workspace_updates: dict
