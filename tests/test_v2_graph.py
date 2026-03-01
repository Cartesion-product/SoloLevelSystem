"""Tests for the v2 Plan-Execute-Observe LangGraph.

Uses mocked LLM and mocked MongoDB to test graph flow without external deps.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from langchain_core.messages import AIMessage, HumanMessage


@pytest_asyncio.fixture
async def mock_mongo_db():
    """Provide a mock MongoDB database."""
    from mongomock_motor import AsyncMongoMockClient
    client = AsyncMongoMockClient()
    db = client["test_solo_leveling"]
    yield db
    client.close()


def _make_mock_chat_model(responses: list[str]):
    """Create a mock LangChain ChatModel that returns predefined responses."""
    mock = MagicMock()
    call_count = 0

    async def mock_ainvoke(messages, **kwargs):
        nonlocal call_count
        idx = min(call_count, len(responses) - 1)
        call_count += 1
        return AIMessage(content=responses[idx])

    mock.ainvoke = mock_ainvoke
    return mock


class TestLoadWorkspaceNode:
    @pytest.mark.asyncio
    async def test_loads_workspace_and_prompts(self, mock_mongo_db):
        """load_workspace node should populate state with workspace data and prompts."""
        from app.domain.workspace.models import SkillRadar, SkillRadarEntry, UserMeta
        from app.domain.workspace.repository import WorkspaceRepository

        # Seed data
        repo = WorkspaceRepository(mock_mongo_db)
        await repo.upsert_profile(UserMeta(user_id="test-user"))
        await repo.upsert_skill_radar("test-user", SkillRadar(entries=[
            SkillRadarEntry(skill_name="Python", score=7.0),
        ]))

        with patch("app.agents.v2.nodes.load_workspace.get_mongo_db", return_value=mock_mongo_db):
            from app.agents.v2.nodes.load_workspace import load_workspace_node

            state = {
                "user_id": "test-user",
                "mode": "technical",
                "target_company": None,
            }
            result = await load_workspace_node(state)

        assert "user_profile" in result
        assert len(result["skill_radar"]) == 1
        assert result["skill_radar"][0]["skill_name"] == "Python"
        assert "system_prompt" in result
        assert "eval_criteria" in result


class TestPlanSessionNode:
    @pytest.mark.asyncio
    async def test_generates_plan(self):
        """plan_session node should produce a training plan."""
        plan_response = json.dumps({
            "target_topics": ["Python", "SQL"],
            "focus_weak_points": ["System Design"],
            "strategy_notes": "Focus on fundamentals first",
            "round_plan": [
                {"round": 1, "topic": "Python", "difficulty": "medium", "goal": "assess"},
            ],
        })

        mock_llm = _make_mock_chat_model([plan_response])

        with patch("app.agents.v2.nodes.plan_session.get_chat_model", return_value=mock_llm):
            from app.agents.v2.nodes.plan_session import plan_session_node

            state = {
                "mode": "technical",
                "weak_points": [{"skill_name": "System Design"}],
                "skill_radar": [{"skill_name": "Python", "score": 7.0}],
                "max_rounds": 5,
                "messages": [],
            }
            result = await plan_session_node(state)

        assert "plan" in result
        assert result["plan"]["target_topics"] == ["Python", "SQL"]
        assert result["current_round"] == 0
        assert len(result["messages"]) == 1


class TestExecuteRoundNode:
    @pytest.mark.asyncio
    async def test_generates_question(self):
        """execute_round node should produce a question and increment round."""
        mock_llm = _make_mock_chat_model(["请问你对Python的GIL有什么理解？"])

        with patch("app.agents.v2.nodes.execute_round.get_chat_model", return_value=mock_llm):
            from app.agents.v2.nodes.execute_round import execute_round_node

            state = {
                "current_round": 0,
                "max_rounds": 5,
                "plan": {
                    "round_plan": [
                        {"round": 1, "topic": "Python GIL", "difficulty": "medium", "goal": "assess"},
                    ],
                },
                "system_prompt": "You are an interviewer.",
                "mode": "technical",
                "messages": [],
            }
            result = await execute_round_node(state)

        assert result["current_round"] == 1
        assert len(result["rounds"]) == 1
        assert result["rounds"][0]["topic"] == "Python GIL"
        assert len(result["messages"]) == 1


class TestObserveAnswerNode:
    @pytest.mark.asyncio
    async def test_evaluates_answer(self):
        """observe_answer node should produce a score and feedback."""
        eval_response = json.dumps({
            "score": 7.5,
            "key_points_hit": ["GIL概念"],
            "key_points_missed": ["多进程替代方案"],
            "gap_identified": None,
            "difficulty_suggestion": "maintain",
            "feedback": "回答不错，但缺少对替代方案的讨论。",
            "skill_updates": [{"skill_name": "Python", "score": 7.5}],
        })

        mock_llm = _make_mock_chat_model([eval_response])

        with patch("app.agents.v2.nodes.observe_answer.get_chat_model", return_value=mock_llm):
            from app.agents.v2.nodes.observe_answer import observe_answer_node

            state = {
                "session_id": "test-session",
                "eval_criteria": "Score 0-10",
                "rounds": [{"question": "What is GIL?", "topic": "Python", "difficulty": "medium"}],
                "messages": [
                    AIMessage(content="What is GIL?"),
                    HumanMessage(content="GIL是Python的全局解释器锁"),
                ],
                "workspace_updates": {},
            }
            result = await observe_answer_node(state)

        assert len(result["round_scores"]) == 1
        assert result["round_scores"][0]["score"] == 7.5
        assert len(result["round_feedbacks"]) == 1


class TestSummarizeSessionNode:
    @pytest.mark.asyncio
    async def test_generates_summary(self):
        """summarize_session node should produce a session summary."""
        summary_response = """总体表现良好，Python基础扎实。
---JSON---
{"overall_score": 7.5, "strengths": ["Python基础"], "weaknesses": ["系统设计"], "recommendations": ["多做设计题"]}"""

        mock_llm = _make_mock_chat_model([summary_response])

        with patch("app.agents.v2.nodes.summarize_session.get_chat_model", return_value=mock_llm):
            from app.agents.v2.nodes.summarize_session import summarize_session_node

            state = {
                "mode": "technical",
                "plan": {},
                "rounds": [{"round": 1}, {"round": 2}],
                "round_scores": [
                    {"score": 8.0, "key_points_hit": ["A"], "key_points_missed": ["B"], "gap_identified": None},
                    {"score": 7.0, "key_points_hit": ["C"], "key_points_missed": [], "gap_identified": "系统设计"},
                ],
                "round_feedbacks": ["Good", "Needs improvement"],
                "messages": [],
            }
            result = await summarize_session_node(state)

        assert "session_summary" in result
        assert result["session_summary"]["overall_score"] == 7.5
        assert "Python基础" in result["session_summary"]["strengths"]
        assert len(result["messages"]) == 1


class TestUpdateWorkspaceNode:
    @pytest.mark.asyncio
    async def test_writes_to_mongodb(self, mock_mongo_db):
        """update_workspace node should persist state to MongoDB."""
        from app.domain.workspace.models import UserMeta
        from app.domain.workspace.repository import WorkspaceRepository

        # Seed a profile
        repo = WorkspaceRepository(mock_mongo_db)
        await repo.upsert_profile(UserMeta(user_id="test-user", total_sessions=0))

        with patch("app.agents.v2.nodes.update_workspace.get_mongo_db", return_value=mock_mongo_db):
            from app.agents.v2.nodes.update_workspace import update_workspace_node

            state = {
                "user_id": "test-user",
                "session_id": "session-1",
                "mode": "technical",
                "target_company": None,
                "current_round": 3,
                "session_summary": {"overall_score": 7.0, "strengths": [], "weaknesses": []},
                "workspace_updates": {
                    "skill_updates": [{"skill_name": "Python", "score": 8.0}],
                    "new_weak_points": [],
                },
            }
            await update_workspace_node(state)

        # Verify data was written
        profile = await repo.get_profile("test-user")
        assert profile.total_sessions == 1

        sessions = await repo.get_sessions("test-user")
        assert len(sessions) == 1
        assert sessions[0].session_id == "session-1"
