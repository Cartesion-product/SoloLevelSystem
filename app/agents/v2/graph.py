"""v2 LangGraph: Plan-Execute-Observe interview loop.

Graph flow:
  START → load_workspace → plan_session → execute_round → END
  (User sends answer via API, graph resumes at observe_answer)
  observe_answer → [should_continue?]
    → execute_round → END  (next question)
    → summarize_session → update_workspace → END  (session complete)
"""

from langgraph.graph import END, StateGraph

from app.agents.v2.nodes.execute_round import execute_round_node
from app.agents.v2.nodes.load_workspace import load_workspace_node
from app.agents.v2.nodes.observe_answer import observe_answer_node
from app.agents.v2.nodes.plan_session import plan_session_node
from app.agents.v2.nodes.summarize_session import summarize_session_node
from app.agents.v2.nodes.update_workspace import update_workspace_node
from app.agents.v2.state import SessionState


def _should_continue_after_observe(state: SessionState) -> str:
    """After observing an answer, decide: next round or wrap up."""
    current = state.get("current_round", 0)
    max_rounds = state.get("max_rounds", 5)
    if current >= max_rounds:
        return "summarize"
    return "continue"


def build_v2_interview_graph() -> StateGraph:
    """Build the v2 Plan-Execute-Observe interview graph.

    The graph has two entry paths:
    1. **Initial invocation** (start_node="load_workspace"):
       load_workspace → plan_session → execute_round → END
       The first question is returned. Graph pauses for user.

    2. **Resume invocation** (start_node="observe_answer"):
       observe_answer → execute_round → END  (or → summarize → update → END)
       Called each time the user sends an answer.
    """
    graph = StateGraph(SessionState)

    # Add all nodes
    graph.add_node("load_workspace", load_workspace_node)
    graph.add_node("plan_session", plan_session_node)
    graph.add_node("execute_round", execute_round_node)
    graph.add_node("observe_answer", observe_answer_node)
    graph.add_node("summarize_session", summarize_session_node)
    graph.add_node("update_workspace", update_workspace_node)

    # --- Path 1: Initial flow ---
    graph.set_entry_point("load_workspace")
    graph.add_edge("load_workspace", "plan_session")
    graph.add_edge("plan_session", "execute_round")
    graph.add_edge("execute_round", END)

    # --- Path 2: After user answers ---
    graph.add_conditional_edges(
        "observe_answer",
        _should_continue_after_observe,
        {
            "continue": "execute_round",
            "summarize": "summarize_session",
        },
    )

    # Summarize → update workspace → END
    graph.add_edge("summarize_session", "update_workspace")
    graph.add_edge("update_workspace", END)

    return graph


def build_v2_initial_graph() -> StateGraph:
    """Graph for the initial session start: load → plan → execute → END."""
    graph = StateGraph(SessionState)
    graph.add_node("load_workspace", load_workspace_node)
    graph.add_node("plan_session", plan_session_node)
    graph.add_node("execute_round", execute_round_node)
    graph.set_entry_point("load_workspace")
    graph.add_edge("load_workspace", "plan_session")
    graph.add_edge("plan_session", "execute_round")
    graph.add_edge("execute_round", END)
    return graph


def build_v2_answer_graph() -> StateGraph:
    """Graph for processing a user answer: observe → (execute|summarize→update) → END."""
    graph = StateGraph(SessionState)
    graph.add_node("observe_answer", observe_answer_node)
    graph.add_node("execute_round", execute_round_node)
    graph.add_node("summarize_session", summarize_session_node)
    graph.add_node("update_workspace", update_workspace_node)
    graph.set_entry_point("observe_answer")
    graph.add_conditional_edges(
        "observe_answer",
        _should_continue_after_observe,
        {
            "continue": "execute_round",
            "summarize": "summarize_session",
        },
    )
    graph.add_edge("execute_round", END)
    graph.add_edge("summarize_session", "update_workspace")
    graph.add_edge("update_workspace", END)
    return graph


# Pre-compiled graph instances
v2_initial_graph = build_v2_initial_graph().compile()
v2_answer_graph = build_v2_answer_graph().compile()
