"""v2 Interview API endpoints with Plan-Execute-Observe loop."""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.agents.v2.graph import v2_answer_graph, v2_initial_graph
from app.api.schemas.interviews_v2 import (
    InterviewChatV2Request,
    InterviewReportV2Response,
    InterviewSessionV2Response,
    InterviewStartV2Request,
    TrainingPlanResponse,
)
from app.dependencies import get_current_user
from app.domain.capability.repository import SkillTreeRepository
from app.domain.interview.models import InterviewSession, User
from app.domain.interview.repository import (
    InterviewSessionRepository,
    ResumeRepository,
    TargetJobRepository,
)
from app.domain.workspace.service import WorkspaceManager
from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import get_db
from app.infrastructure.mongodb import get_mongo_db

router = APIRouter(prefix="/v2/interviews", tags=["v2-interviews"])

SESSION_STATE_PREFIX = "v2_interview_state:"
SESSION_TTL = 7 * 24 * 3600  # 7 days


@router.post("/start", response_model=InterviewSessionV2Response, status_code=status.HTTP_201_CREATED)
async def start_interview_v2(
    body: InterviewStartV2Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new v2 interview session with Plan-Execute-Observe."""
    resume_repo = ResumeRepository(db)
    job_repo = TargetJobRepository(db)

    # Load resume
    resume = None
    if body.resume_id:
        resume = await resume_repo.get_by_id(uuid.UUID(body.resume_id))
    else:
        resume = await resume_repo.get_default(user.id)
    if not resume:
        raise HTTPException(status_code=400, detail="No resume found. Please upload a resume first.")

    # Load job
    job = None
    if body.job_id:
        job = await job_repo.get_by_id(uuid.UUID(body.job_id))
    else:
        job = await job_repo.get_default(user.id)

    # Initialize workspace from v1 data if needed
    try:
        mongo_db = get_mongo_db()
        manager = WorkspaceManager(mongo_db)
        await manager.initialize_from_v1(str(user.id), db)
    except Exception:
        pass  # MongoDB may be unavailable in dev

    # Create session in DB
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.create(
        user_id=user.id,
        resume_id=resume.id,
        job_id=job.id if job else None,
        session_type="simulated_v2",
        mode=body.mode,
        target_company=body.target_company,
    )

    # Build initial state
    initial_state = {
        "user_id": str(user.id),
        "session_id": str(session.id),
        "user_profile": {},
        "skill_radar": [],
        "weak_points": [],
        "mode": body.mode,
        "target_company": body.target_company,
        "system_prompt": "",
        "eval_criteria": "",
        "plan": {},
        "rounds": [],
        "current_round": 0,
        "max_rounds": body.max_rounds,
        "messages": [],
        "round_scores": [],
        "round_feedbacks": [],
        "session_summary": {},
        "workspace_updates": {},
    }

    # Run initial graph: load_workspace → plan_session → execute_round
    result = await v2_initial_graph.ainvoke(initial_state)

    # Cache state
    state_to_cache = _serialize_state(result)
    await cache_set(f"{SESSION_STATE_PREFIX}{session.id}", state_to_cache, SESSION_TTL)

    # Extract first AI message (the question)
    first_msg = None
    ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
    if ai_messages:
        first_msg = ai_messages[-1].content

    # Build plan response
    plan = result.get("plan", {})
    plan_response = TrainingPlanResponse(
        plan_id=plan.get("plan_id"),
        target_topics=plan.get("target_topics", []),
        focus_weak_points=plan.get("focus_weak_points", []),
        strategy_notes=plan.get("strategy_notes", ""),
        round_plan=plan.get("round_plan", []),
    )

    return InterviewSessionV2Response(
        id=str(session.id),
        status=session.status,
        mode=body.mode,
        target_company=body.target_company,
        question_count=result.get("current_round", 0),
        max_rounds=body.max_rounds,
        first_message=first_msg,
        training_plan=plan_response,
        created_at=session.created_at,
    )


@router.post("/{session_id}/chat")
async def chat_v2(
    session_id: str,
    body: InterviewChatV2Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message in the v2 interview, returns SSE stream."""
    # Verify session
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session is not active")

    # Load state
    cached = await cache_get(f"{SESSION_STATE_PREFIX}{session_id}")
    if not cached:
        raise HTTPException(status_code=400, detail="Session state expired")

    state = _deserialize_state(cached)

    # Add user's answer
    state["messages"] = state.get("messages", []) + [HumanMessage(content=body.message)]

    async def event_generator():
        yield {"event": "thinking", "data": json.dumps({"status": "evaluating"})}

        # Run answer graph: observe_answer → execute_round (or → summarize → update)
        result = await v2_answer_graph.ainvoke(state)

        # SSE: metadata
        yield {
            "event": "metadata",
            "data": json.dumps({
                "mode": result.get("mode"),
                "current_round": result.get("current_round"),
                "max_rounds": result.get("max_rounds"),
            }),
        }

        # SSE: round evaluation
        scores = result.get("round_scores", [])
        if scores:
            latest_score = scores[-1]
            yield {
                "event": "evaluation",
                "data": json.dumps({
                    "score": latest_score.get("score"),
                    "feedback": latest_score.get("feedback", ""),
                }),
            }

        # Extract AI response
        ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
        if ai_messages:
            last_ai = ai_messages[-1].content
            chunk_size = 20
            for i in range(0, len(last_ai), chunk_size):
                yield {"event": "chunk", "data": json.dumps({"content": last_ai[i:i + chunk_size]})}

        # Cache updated state
        state_to_cache = _serialize_state(result)
        await cache_set(f"{SESSION_STATE_PREFIX}{session_id}", state_to_cache, SESSION_TTL)

        # Update DB
        await session_repo.update(
            uuid.UUID(session_id),
            question_count=result.get("current_round", 0),
        )

        # Check if session ended (summarize node ran)
        summary = result.get("session_summary", {})
        if summary and isinstance(summary, dict) and summary.get("overall_score") is not None:
            await session_repo.update(
                uuid.UUID(session_id),
                status="completed",
                summary=summary,
                completed_at=datetime.now(timezone.utc),
            )
            yield {"event": "session_end", "data": json.dumps(summary)}

            # Trigger async post-processing
            try:
                from app.tasks.post_interview import process_session
                conversation = [
                    {"type": "human" if isinstance(m, HumanMessage) else "ai", "content": m.content}
                    for m in result.get("messages", [])
                ]
                process_session.delay(
                    session_id, str(user.id), conversation, state_to_cache,
                )
            except Exception:
                pass
        else:
            yield {"event": "done", "data": json.dumps({"status": "ok"})}

    return EventSourceResponse(event_generator())


@router.post("/{session_id}/end", response_model=InterviewSessionV2Response)
async def end_interview_v2(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually end a v2 interview session."""
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    session = await session_repo.update(
        uuid.UUID(session_id),
        status="completed",
        completed_at=datetime.now(timezone.utc),
    )

    return InterviewSessionV2Response(
        id=str(session.id),
        status=session.status,
        mode=getattr(session, "mode", "technical") or "technical",
        target_company=getattr(session, "target_company", None),
        question_count=session.question_count,
        max_rounds=5,
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


@router.get("/{session_id}/report", response_model=InterviewReportV2Response)
async def get_report_v2(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the v2 interview report."""
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    return InterviewReportV2Response(
        session_id=str(session.id),
        status=session.status,
        mode=getattr(session, "mode", "technical") or "technical",
        target_company=getattr(session, "target_company", None),
        summary=session.summary,
        question_count=session.question_count,
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


def _serialize_state(state: dict) -> dict:
    """Serialize SessionState for Redis storage."""
    serialized = {}
    for k, v in state.items():
        if k == "messages":
            serialized[k] = [
                {"type": "human" if isinstance(m, HumanMessage) else "ai", "content": m.content}
                for m in v
            ]
        else:
            serialized[k] = v
    return serialized


def _deserialize_state(data: dict) -> dict:
    """Deserialize SessionState from Redis storage."""
    state = dict(data)
    if "messages" in state:
        state["messages"] = [
            HumanMessage(content=m["content"]) if m["type"] == "human" else AIMessage(content=m["content"])
            for m in state["messages"]
        ]
    return state
