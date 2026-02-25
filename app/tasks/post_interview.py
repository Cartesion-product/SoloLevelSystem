"""Post-interview async tasks: summary generation, psychology analysis, quest generation."""

import asyncio
import json
import uuid
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app


def _run_async(coro):
    """Helper to run async code from synchronous Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="post_interview.process_session")
def process_session(session_id: str, user_id: str, conversation_messages: list[dict], state_data: dict):
    """Main post-interview task that orchestrates all async processing."""
    _run_async(_process_session_async(session_id, user_id, conversation_messages, state_data))


async def _process_session_async(session_id: str, user_id: str, conversation_messages: list[dict], state_data: dict):
    """Async implementation of post-interview processing."""
    from sqlalchemy import select

    from app.agents.nodes.psycho_analyst import analyze_psychology
    from app.agents.nodes.quest_master import generate_quests
    from app.domain.capability.models import SkillTree
    from app.domain.growth.models import MoodLog, QuestLog, UserPsychologyProfile
    from app.domain.interview.models import InterviewSession
    from app.infrastructure.cache import cache_set
    from app.infrastructure.database import async_session_factory
    from app.infrastructure.embedding import get_embedding_provider
    from app.infrastructure.llm_provider import get_llm_provider
    from app.infrastructure.vector_store import (
        CONVERSATION_MEMORY_COLLECTION,
        upsert_vectors,
    )

    llm = get_llm_provider()

    async with async_session_factory() as db:
        # 1. Generate session summary (warm layer)
        summary = state_data.get("session_summary", "")
        if isinstance(summary, str):
            try:
                summary = json.loads(summary)
            except (json.JSONDecodeError, TypeError):
                summary = {"summary_text": summary}

        session_result = await db.execute(
            select(InterviewSession).where(InterviewSession.id == uuid.UUID(session_id))
        )
        session = session_result.scalar_one_or_none()
        if session:
            session.summary = summary
            session.status = "completed"
            session.completed_at = datetime.now(timezone.utc)

        # 2. Psychology analysis
        profile_result = await db.execute(
            select(UserPsychologyProfile).where(UserPsychologyProfile.user_id == uuid.UUID(user_id))
        )
        profile = profile_result.scalar_one_or_none()
        if not profile:
            profile = UserPsychologyProfile(user_id=uuid.UUID(user_id))
            db.add(profile)
            await db.flush()

        current_profile = {
            "confidence_score": profile.confidence_score,
            "resilience_score": profile.resilience_score,
            "personality_tags": profile.personality_tags or [],
        }

        psych_result = await analyze_psychology(conversation_messages, current_profile, llm)

        # Update profile
        profile.confidence_score = max(0.0, min(1.0,
            profile.confidence_score + psych_result.get("confidence_delta", 0.0)))
        profile.resilience_score = max(0.0, min(1.0,
            profile.resilience_score + psych_result.get("resilience_delta", 0.0)))
        profile.personality_tags = psych_result.get("personality_tags", profile.personality_tags)
        profile.daily_motivation = psych_result.get("daily_motivation", profile.daily_motivation)

        # Add mood log
        mood = MoodLog(
            user_id=uuid.UUID(user_id),
            session_id=uuid.UUID(session_id),
            detected_mood=psych_result.get("detected_mood", "neutral"),
            trigger_event=psych_result.get("trigger_event"),
        )
        db.add(mood)

        # 3. Quest generation
        identified_gaps = state_data.get("identified_gaps", [])
        skill_tree_snapshot = state_data.get("skill_tree_snapshot", [])

        quests = await generate_quests(identified_gaps, skill_tree_snapshot, llm)

        for q in quests:
            quest = QuestLog(
                user_id=uuid.UUID(user_id),
                session_id=uuid.UUID(session_id),
                quest_title=q.get("quest_title", "Learning task"),
                quest_detail=q.get("quest_detail", ""),
                verification_method=q.get("verification_method", "verbal_quiz"),
            )
            db.add(quest)

        # 4. Update skill tree scores based on evaluation
        for gap in identified_gaps:
            skill_name = gap.get("skill", "")
            if skill_name:
                skill_result = await db.execute(
                    select(SkillTree).where(
                        SkillTree.user_id == uuid.UUID(user_id),
                        SkillTree.skill_name == skill_name,
                    )
                )
                skill = skill_result.scalar_one_or_none()
                if skill:
                    skill.assess_count += 1
                    new_score = gap.get("score", skill.proficiency_score)
                    # Weighted average with existing score
                    if skill.assess_count > 1:
                        skill.proficiency_score = round(
                            (skill.proficiency_score * (skill.assess_count - 1) + new_score) / skill.assess_count
                        )
                    else:
                        skill.proficiency_score = round(new_score)
                    skill.proficiency_score = max(0, min(10, skill.proficiency_score))
                    skill.last_assessed_at = datetime.now(timezone.utc)
                    skill.source_type = "verified"

        await db.commit()

        # 5. Cold layer: vectorize valuable conversation fragments
        try:
            embedding = get_embedding_provider()
            fragments = []
            for m in conversation_messages:
                content = m.get("content", "")
                if len(content) > 50:  # Only meaningful messages
                    fragments.append(m)

            if fragments:
                texts = [f["content"][:500] for f in fragments]
                vectors = await embedding.embed(texts)

                ids = [str(uuid.uuid4()) for _ in fragments]
                payloads = [
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "speaker": "user" if f.get("type") == "human" else "interviewer",
                        "content": f.get("content", "")[:500],
                        "topic": state_data.get("current_topic", ""),
                    }
                    for f in fragments
                ]

                upsert_vectors(CONVERSATION_MEMORY_COLLECTION, ids, vectors, payloads)
        except Exception:
            pass  # Vector storage failure shouldn't break the task

        # 6. Update Redis cache with recent session summaries
        recent_key = f"recent_summaries:{user_id}"
        await cache_set(recent_key, json.dumps(summary, ensure_ascii=False), 7 * 24 * 3600)
