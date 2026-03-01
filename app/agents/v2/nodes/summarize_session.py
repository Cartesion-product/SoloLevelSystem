"""Node: summarize_session — Generate overall session summary.

LLM call at low temperature (0.3) for consistent summarization.
"""

import json

from langchain_core.messages import AIMessage, SystemMessage

from app.agents.v2.state import SessionState
from app.infrastructure.llm_provider import get_chat_model


async def summarize_session_node(state: SessionState) -> dict:
    """Produce a summary of the entire interview session."""
    llm = get_chat_model(temperature=0.3)

    round_scores = state.get("round_scores", [])
    round_feedbacks = state.get("round_feedbacks", [])
    rounds = state.get("rounds", [])
    mode = state.get("mode", "technical")
    plan = state.get("plan", {})

    # Compute aggregate stats
    scores = [s.get("score", 0) for s in round_scores]
    avg_score = sum(scores) / max(len(scores), 1)

    all_hits = []
    all_misses = []
    all_gaps = []
    for s in round_scores:
        all_hits.extend(s.get("key_points_hit", []))
        all_misses.extend(s.get("key_points_missed", []))
        gap = s.get("gap_identified")
        if gap:
            all_gaps.append(gap)

    summary_prompt = f"""Summarize this mock interview session.

Mode: {mode}
Rounds completed: {len(rounds)}
Average score: {avg_score:.1f}/10
Strengths observed: {', '.join(list(set(all_hits))[:10]) or 'N/A'}
Gaps observed: {', '.join(list(set(all_gaps))[:10]) or 'N/A'}
Round-by-round feedback: {json.dumps(round_feedbacks, ensure_ascii=False)[:1000]}

Generate a comprehensive but concise summary in Chinese. Include:
1. 总体评价 (overall assessment)
2. 亮点 (strengths, 2-3 items)
3. 需要改进 (areas for improvement, 2-3 items)
4. 学习建议 (2-3 specific recommendations)

Also output a structured JSON for storage:
{{
  "overall_score": {avg_score:.1f},
  "strengths": [...],
  "weaknesses": [...],
  "gaps": [...],
  "recommendations": [...]
}}

Output the Chinese summary first, then a line "---JSON---", then the JSON."""

    response = await llm.ainvoke([
        SystemMessage(content=summary_prompt),
    ])

    content = response.content or ""

    # Parse structured summary
    summary_dict = {
        "overall_score": round(avg_score, 1),
        "strengths": list(set(all_hits))[:10],
        "weaknesses": list(set(all_misses))[:10],
        "gaps": list(set(all_gaps)),
        "round_count": len(rounds),
    }

    if "---JSON---" in content:
        text_part, json_part = content.split("---JSON---", 1)
        try:
            parsed = json.loads(json_part.strip())
            summary_dict.update(parsed)
        except (json.JSONDecodeError, TypeError):
            pass
        display_text = text_part.strip()
    else:
        display_text = content

    return {
        "session_summary": summary_dict,
        "messages": [AIMessage(content=display_text)],
    }
