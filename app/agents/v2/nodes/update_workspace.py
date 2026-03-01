"""Node: update_workspace — Write session results back to MongoDB.

No LLM call. Pure I/O: writes accumulated state to workspace.
"""

from app.agents.v2.state import SessionState
from app.domain.workspace.service import WorkspaceManager
from app.infrastructure.mongodb import get_mongo_db


async def update_workspace_node(state: SessionState) -> dict:
    """Persist session results to MongoDB workspace."""
    db = get_mongo_db()
    manager = WorkspaceManager(db)

    user_id = state["user_id"]
    await manager.update_after_session(user_id, state)

    return {}
