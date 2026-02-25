"""LangGraph main graph definition for the interview flow."""

from langgraph.graph import END, StateGraph

from app.agents.nodes.evaluator import evaluator_node
from app.agents.nodes.interviewer import interviewer_node
from app.agents.nodes.strategist import strategist_node
from app.agents.state import InterviewState


def should_continue(state: InterviewState) -> str:
    """Route after evaluator: continue or end."""
    if state.get("next_action") == "end" or state.get("phase") == "feedback":
        return "feedback"
    return "strategist"


def after_interviewer(state: InterviewState) -> str:
    """Route after interviewer: wait for user input or end."""
    if state.get("next_action") == "end" or state.get("phase") == "feedback":
        return END
    return "wait_for_user"


def build_interview_graph() -> StateGraph:
    """Build the interview LangGraph state machine.

    Flow:
        init → strategist → interviewer → (wait for user) → evaluator → strategist → ...
        When max questions reached or end signal → interviewer generates feedback → END
    """
    graph = StateGraph(InterviewState)

    # Add nodes
    graph.add_node("strategist", strategist_node)
    graph.add_node("interviewer", interviewer_node)
    graph.add_node("evaluator", evaluator_node)
    graph.add_node("feedback", _feedback_node)

    # Entry point
    graph.set_entry_point("strategist")

    # Edges
    graph.add_edge("strategist", "interviewer")
    graph.add_conditional_edges(
        "interviewer",
        after_interviewer,
        {"wait_for_user": END, END: END},
    )

    # Evaluator routes back to strategist or to feedback
    graph.add_conditional_edges(
        "evaluator",
        should_continue,
        {"strategist": "strategist", "feedback": "feedback"},
    )

    # Feedback ends the graph
    graph.add_edge("feedback", END)

    return graph


async def _feedback_node(state: InterviewState) -> dict:
    """Generate feedback and end. Delegates to interviewer's feedback logic."""
    state_copy = dict(state)
    state_copy["phase"] = "feedback"
    state_copy["next_action"] = "end"
    from app.agents.nodes.interviewer import interviewer_node
    return await interviewer_node(state_copy)


# Compiled graph instance
interview_graph = build_interview_graph().compile()
