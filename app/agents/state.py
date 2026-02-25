"""InterviewState definition for LangGraph."""

from typing import Annotated, Any, Literal

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class InterviewState(TypedDict):
    # --- Base context ---
    user_id: str
    session_id: str
    resume_context: dict
    jd_context: dict
    skill_tree_snapshot: list[dict]
    pending_quests: list[dict]

    # --- Live conversation ---
    messages: Annotated[list[BaseMessage], add_messages]
    current_topic: str
    question_count: int
    max_questions: int

    # --- Strategy control ---
    stress_level: float
    silence_count: int
    phase: Literal["defense", "attack", "feedback"]
    difficulty: Literal["easy", "medium", "hard", "expert"]

    # --- Routing ---
    next_action: str  # "ask_question", "icebreak", "switch_phase", "end"
    interviewer_directive: str  # Instructions from strategist to interviewer

    # --- Analysis results ---
    identified_gaps: list[dict]
    evaluation_scores: list[dict]
    session_summary: str
    current_evaluation: dict  # Latest evaluator output
