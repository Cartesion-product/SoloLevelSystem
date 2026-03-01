"""Node: load_workspace — Load MongoDB workspace + apply PromptPluginLoader.

No LLM call. Pure I/O: reads workspace state and merges prompt plugins.
"""

from app.agents.prompt_loader import PromptPluginLoader
from app.agents.v2.state import SessionState
from app.domain.workspace.service import WorkspaceManager
from app.infrastructure.mongodb import get_mongo_db


async def load_workspace_node(state: SessionState) -> dict:
    """Load workspace data and prompt configuration into state."""
    db = get_mongo_db()
    manager = WorkspaceManager(db)

    # Load workspace state
    ws = await manager.load_for_session(state["user_id"])

    # Load prompts via plugin system
    loader = PromptPluginLoader()
    mode = state.get("mode", "technical")
    target = state.get("target_company")

    system_prompt = loader.load_system_prompt(mode, target)
    eval_criteria = loader.load_eval_criteria(mode)

    return {
        "user_profile": ws["user_profile"],
        "skill_radar": ws["skill_radar"],
        "weak_points": ws["weak_points"],
        "system_prompt": system_prompt,
        "eval_criteria": eval_criteria,
    }
