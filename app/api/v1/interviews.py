"""Interview API endpoints with SSE streaming."""

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from fastapi.responses import Response

from app.agents.graph import interview_graph
from app.agents.state import InterviewState
from app.api.schemas.interviews import (
    InterviewChatRequest,
    InterviewReportResponse,
    InterviewSessionResponse,
    InterviewStartRequest,
)
from app.core.logger import get_logger
from app.dependencies import get_current_user
from app.domain.capability.repository import SkillTreeRepository
from app.domain.interview.models import User
from app.domain.interview.repository import (
    InterviewSessionRepository,
    ResumeRepository,
    TargetJobRepository,
)
from app.domain.workspace.service import WorkspaceManager
from app.infrastructure.cache import cache_get, cache_set
from app.infrastructure.database import get_db
from app.infrastructure.pdf_generator import generate_transcript_pdf

logger = get_logger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])

SESSION_STATE_PREFIX = "interview_state:"
SESSION_TTL = 7 * 24 * 3600  # 7 days


@router.post("/start", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    body: InterviewStartRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initialize a new interview session."""
    resume_repo = ResumeRepository(db)
    job_repo = TargetJobRepository(db)
    skill_repo = SkillTreeRepository(db)

    # Load resume (specified or default)
    resume = None
    if body.resume_id:
        resume = await resume_repo.get_by_id(uuid.UUID(body.resume_id))
    else:
        resume = await resume_repo.get_default(user.id)

    if not resume:
        raise HTTPException(status_code=400, detail="No resume found. Please upload a resume first.")

    # Load job (specified or default)
    job = None
    if body.job_id:
        job = await job_repo.get_by_id(uuid.UUID(body.job_id))
    else:
        job = await job_repo.get_default(user.id)

    # Load skill tree
    skills = await skill_repo.get_by_user(user.id)
    skill_snapshot = [
        {
            "id": str(s.id),
            "skill_name": s.skill_name,
            "proficiency_score": s.proficiency_score,
            "source_type": s.source_type,
            "focus_status": s.focus_status,
        }
        for s in skills
    ]

    # Create session in DB
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.create(
        user_id=user.id,
        resume_id=resume.id,
        job_id=job.id if job else None,
        session_type="simulated",
    )

    # Initialize interview state
    initial_state: InterviewState = {
        "user_id": str(user.id),
        "session_id": str(session.id),
        "resume_context": resume.parsed_data or {},
        "jd_context": job.parsed_requirements or {} if job else {},
        "skill_tree_snapshot": skill_snapshot,
        "pending_quests": [],
        "messages": [],
        "current_topic": "",
        "question_count": 0,
        "max_questions": body.max_questions,
        "stress_level": 0.3,
        "silence_count": 0,
        "phase": "defense",
        "difficulty": "medium",
        "next_action": "ask_question",
        "interviewer_directive": "Start by introducing yourself briefly, then ask the first question about a project from the candidate's resume.",
        "identified_gaps": [],
        "evaluation_scores": [],
        "session_summary": "",
        "current_evaluation": {},
    }

    # Run initial strategist → interviewer to get first question
    result = await interview_graph.ainvoke(initial_state)

    # Cache state in Redis
    state_to_cache = _serialize_state(result)
    await cache_set(f"{SESSION_STATE_PREFIX}{session.id}", state_to_cache, SESSION_TTL)

    # Extract first AI message
    first_msg = None
    for m in result.get("messages", []):
        if isinstance(m, AIMessage):
            first_msg = m.content
            break

    # Save first AI message to transcript
    if first_msg:
        await session_repo.update(
            session.id,
            transcript=[{"role": "ai", "content": first_msg}],
        )

    # Initialize workspace (best-effort, requires MongoDB)
    try:
        from app.infrastructure.mongodb import get_mongo_db
        mongo_db = get_mongo_db()
        workspace_mgr = WorkspaceManager(mongo_db)
        await workspace_mgr.initialize_from_v1(str(user.id), db)
    except Exception as ws_err:
        logger.warning(f"Failed to initialize workspace: {ws_err}")

    return InterviewSessionResponse(
        id=str(session.id),
        status=session.status,
        session_type=session.session_type,
        question_count=result.get("question_count", 0),
        first_message=first_msg,
        created_at=session.created_at,
    )


@router.post("/{session_id}/chat")
async def chat(
    session_id: str,
    body: InterviewChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message in the interview, returns SSE stream."""
    # Verify session ownership
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session is not active")

    # Load state from Redis
    cached = await cache_get(f"{SESSION_STATE_PREFIX}{session_id}")
    if not cached:
        raise HTTPException(status_code=400, detail="Session state expired")

    state = _deserialize_state(cached)

    # Add user message
    state["messages"] = state.get("messages", []) + [HumanMessage(content=body.message)]

    async def event_generator():
        try:
            # SSE: thinking event
            yield {"event": "thinking", "data": json.dumps({"status": "evaluating"})}

            # Run evaluator on user's answer
            from app.agents.nodes.evaluator import evaluator_node
            eval_result = await evaluator_node(state)
            for k, v in eval_result.items():
                state[k] = v

            # SSE: metadata
            yield {
                "event": "metadata",
                "data": json.dumps({
                    "phase": state.get("phase"),
                    "difficulty": state.get("difficulty"),
                    "question_count": state.get("question_count"),
                    "stress_level": state.get("stress_level"),
                }),
            }

            # Check if should end
            if state.get("question_count", 0) >= state.get("max_questions", 8):
                state["next_action"] = "end"
                state["phase"] = "feedback"

            # Run strategist → interviewer
            yield {"event": "thinking", "data": json.dumps({"status": "generating"})}

            result = await interview_graph.ainvoke(state)

            # Extract AI response
            ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
            last_ai_content = ""
            if ai_messages:
                last_ai_content = ai_messages[-1].content
                # Stream chunks
                chunk_size = 20
                for i in range(0, len(last_ai_content), chunk_size):
                    yield {"event": "chunk", "data": json.dumps({"content": last_ai_content[i:i + chunk_size]})}

            # Update state
            state_to_cache = _serialize_state(result)
            await cache_set(f"{SESSION_STATE_PREFIX}{session_id}", state_to_cache, SESSION_TTL)

            # Save transcript: user answer + AI question
            transcript_entries = [
                {"role": "user", "content": body.message},
            ]
            if last_ai_content:
                transcript_entries.append({"role": "ai", "content": last_ai_content})
            await _append_transcript(session_repo, session_id, transcript_entries)

            # Update DB
            await session_repo.update(
                uuid.UUID(session_id),
                question_count=result.get("question_count", 0),
            )

            if result.get("phase") == "feedback" or result.get("next_action") == "end":
                # Session complete
                summary = {}
                if result.get("session_summary"):
                    try:
                        summary = json.loads(result["session_summary"])
                    except (json.JSONDecodeError, TypeError):
                        summary = {"summary_text": result.get("session_summary", "")}

                await session_repo.update(
                    uuid.UUID(session_id),
                    status="completed",
                    summary=summary,
                    completed_at=datetime.now(timezone.utc),
                )

                # Auto-save PDF transcript
                try:
                    await _auto_save_transcript_pdf(session_repo, session_id, str(user.id))
                except Exception as pdf_err:
                    logger.warning(f"Failed to auto-save transcript PDF: {pdf_err}")

                # Update workspace (best-effort)
                try:
                    from app.infrastructure.mongodb import get_mongo_db
                    mongo_db = get_mongo_db()
                    workspace_mgr = WorkspaceManager(mongo_db)
                    await workspace_mgr.update_after_session(str(user.id), result)
                except Exception as ws_err:
                    logger.warning(f"Failed to update workspace after session: {ws_err}")

                yield {"event": "session_end", "data": json.dumps(summary)}
            else:
                yield {"event": "done", "data": json.dumps({"status": "ok"})}
        except Exception as e:
            logger.error(f"Interview SSE error: {e}", exc_info=True)
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_generator(), ping=15)


@router.post("/{session_id}/end", response_model=InterviewSessionResponse)
async def end_interview(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually end an interview session."""
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    session = await session_repo.update(
        uuid.UUID(session_id),
        status="completed",
        completed_at=datetime.now(timezone.utc),
    )

    return InterviewSessionResponse(
        id=str(session.id),
        status=session.status,
        session_type=session.session_type,
        question_count=session.question_count,
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


@router.get("/{session_id}/report", response_model=InterviewReportResponse)
async def get_report(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the interview report."""
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    return InterviewReportResponse(
        session_id=str(session.id),
        status=session.status,
        summary=session.summary,
        question_count=session.question_count,
        duration_seconds=session.duration_seconds,
        created_at=session.created_at,
        completed_at=session.completed_at,
    )


def _serialize_state(state: dict) -> dict:
    """Serialize InterviewState for Redis storage."""
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
    """Deserialize InterviewState from Redis storage."""
    state = dict(data)
    if "messages" in state:
        state["messages"] = [
            HumanMessage(content=m["content"]) if m["type"] == "human" else AIMessage(content=m["content"])
            for m in state["messages"]
        ]
    return state


async def _append_transcript(
    session_repo: InterviewSessionRepository,
    session_id: str,
    entries: list[dict],
) -> None:
    """Append entries to the session's transcript JSONB field."""
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session:
        return
    existing = session.transcript or []
    existing.extend(entries)
    await session_repo.update(uuid.UUID(session_id), transcript=existing)


async def _auto_save_transcript_pdf(
    session_repo: InterviewSessionRepository,
    session_id: str,
    user_id: str,
) -> None:
    """Generate and save transcript PDF to disk."""
    from app.config import BASE_DIR

    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or not session.transcript:
        return

    pdf_bytes = generate_transcript_pdf(
        transcript=session.transcript,
        session_date=session.created_at,
    )

    pdf_dir = BASE_DIR / "uploads" / "transcripts" / user_id
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / f"{session_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    logger.info(f"Transcript PDF saved: {pdf_path}")


@router.get("/{session_id}/transcript/pdf")
async def download_transcript_pdf(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download the interview transcript as a PDF."""
    session_repo = InterviewSessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    transcript = session.transcript or []
    if not transcript:
        raise HTTPException(status_code=404, detail="No transcript available")

    pdf_bytes = generate_transcript_pdf(
        transcript=transcript,
        session_date=session.created_at,
    )

    filename = f"interview_{session_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
