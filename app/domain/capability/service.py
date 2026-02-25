"""Skill tree service: auto-generate from resume, detect gaps from JD."""

import json
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.domain.capability.repository import SkillAdviceRepository, SkillTreeRepository
from app.infrastructure.llm_provider import BaseLLMProvider

logger = get_logger(__name__)

SKILL_SCORING_PROMPT = """你是一位资深技术面试官。请根据以下简历的 **项目经验、工作职责、技术使用场景** 对候选人的每项技能进行 0-10 评分。

## 评分标准（必须严格区分，禁止全部给相近分数）

| 分数 | 含义 | 判断依据 |
|------|------|----------|
| 0-1 | 几乎无经验 | 简历中完全没有提及该技能的使用场景 |
| 2-3 | 了解概念 | 仅在技能列表中出现，无实际项目佐证 |
| 4-5 | 基础使用 | 在 1 个项目中有简单使用，描述笼统 |
| 6-7 | 熟练应用 | 在多个项目中使用，有具体的技术细节描述（如架构设计、性能优化、问题解决） |
| 8-9 | 深度精通 | 作为核心技术栈在复杂场景中深度应用，有量化成果（如提升 XX%、支撑 XX 量级） |
| 10  | 专家级 | 有开源贡献、技术文章、或在该领域有公认的专业成就 |

## 评分要点
- **看项目描述而非技能列表**：技能列表里写了但项目中没用过 → 2-3 分
- **看使用深度**：只是"使用了 XX"→ 4-5 分；"用 XX 实现了 YY，解决了 ZZ 问题"→ 6-8 分
- **看使用广度**：只在一个项目中出现 vs 多个项目反复使用
- **看量化成果**：有具体数据支撑的技能应获得更高分
- **分数要有区分度**：不同技能的掌握程度不同，分数必须拉开差距

## 简历详细信息

### 技能清单
{skills_section}

### 项目经验
{projects_section}

### 工作经历
{work_section}

## 待评分技能列表
{skill_list}

## 输出要求
严格返回 JSON，key 必须与待评分技能列表中的名称 **完全一致**（包括大小写），不要添加任何额外文字：
{{"技能名": {{"score": 7, "comment": "在XX项目中用于YY场景，有ZZ成果"}}}}
"""


def _build_resume_detail(parsed_data: dict[str, Any]) -> dict[str, str]:
    """从 parsed_data 中提取详细的简历信息用于评分。"""
    # 技能清单
    skills_section = parsed_data.get("skills", {})
    skills_text = json.dumps(skills_section, ensure_ascii=False, indent=2) if skills_section else "无"

    # 项目经验 - 尽量提取所有细节
    projects_parts = []
    for i, proj in enumerate(parsed_data.get("projects", []), 1):
        name = proj.get("name", proj.get("project_name", "未命名项目"))
        tech = proj.get("tech_stack", [])
        desc = proj.get("description", "")
        # 尝试多种字段名
        responsibilities = proj.get("responsibilities", proj.get("highlights", proj.get("details", "")))
        if isinstance(responsibilities, list):
            responsibilities = "\n  - ".join(responsibilities)
        role = proj.get("role", "")
        parts = [f"{i}. **{name}**"]
        if role:
            parts.append(f"   角色: {role}")
        if tech:
            parts.append(f"   技术栈: {', '.join(tech) if isinstance(tech, list) else tech}")
        if desc:
            parts.append(f"   描述: {desc}")
        if responsibilities:
            parts.append(f"   职责/亮点: {responsibilities}")
        projects_parts.append("\n".join(parts))
    projects_text = "\n\n".join(projects_parts) if projects_parts else "无项目经验"

    # 工作经历
    work_parts = []
    for i, exp in enumerate(parsed_data.get("work_experience", []), 1):
        company = exp.get("company", "未知公司")
        role = exp.get("role", exp.get("position", ""))
        period = exp.get("period", exp.get("duration", ""))
        desc = exp.get("description", "")
        responsibilities = exp.get("responsibilities", exp.get("highlights", exp.get("details", "")))
        if isinstance(responsibilities, list):
            responsibilities = "\n  - ".join(responsibilities)
        parts = [f"{i}. **{company}** - {role}"]
        if period:
            parts.append(f"   时间: {period}")
        if desc:
            parts.append(f"   描述: {desc}")
        if responsibilities:
            parts.append(f"   职责: {responsibilities}")
        work_parts.append("\n".join(parts))
    work_text = "\n\n".join(work_parts) if work_parts else "无工作经历"

    return {
        "skills_section": skills_text,
        "projects_section": projects_text,
        "work_section": work_text,
    }


async def _score_skills_with_llm(
    llm: BaseLLMProvider,
    parsed_data: dict[str, Any],
    skill_names: list[str],
) -> dict[str, dict]:
    """Call LLM to score a list of skills based on resume data. Returns {name: {score, comment}}."""
    if not skill_names:
        return {}

    detail = _build_resume_detail(parsed_data)

    prompt = SKILL_SCORING_PROMPT.format(
        skills_section=detail["skills_section"],
        projects_section=detail["projects_section"],
        work_section=detail["work_section"],
        skill_list=json.dumps(skill_names, ensure_ascii=False),
    )

    try:
        response = await llm.chat(
            [{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        # Strip markdown code blocks if present
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        raw_scores = json.loads(text)
        logger.info(f"LLM skill scoring returned {len(raw_scores)} scores")

        # Build case-insensitive lookup for robustness
        lower_map: dict[str, dict] = {}
        for k, v in raw_scores.items():
            lower_map[k.strip().lower()] = v

        # Map back to original skill names
        scores: dict[str, dict] = {}
        for name in skill_names:
            key = name.strip().lower()
            if key in lower_map:
                entry = lower_map[key]
                # Clamp score to 0-10
                score = entry.get("score", 5)
                if isinstance(score, (int, float)):
                    score = max(0, min(10, int(round(score))))
                else:
                    score = 5
                scores[name] = {"score": score, "comment": entry.get("comment", "")}

        logger.info(f"Mapped {len(scores)}/{len(skill_names)} skill scores")
        return scores
    except json.JSONDecodeError as e:
        logger.warning(f"LLM skill scoring JSON parse failed: {e}\nRaw response: {response[:500]}")
        return {}
    except Exception as e:
        logger.warning(f"LLM skill scoring failed: {e}", exc_info=True)
        return {}


SKILL_ADVICE_PROMPT = """你是一位资深技术职业导师。根据以下候选人的技能评估结果，给出两条简短、有针对性的中文建议。

## 技能分类及平均分（满分 10）
{category_scores}

## 要求
请返回严格 JSON，不要添加任何额外文字：
{{"strength_advice": "针对最强领域(分数最高的分类)的深耕建议，1-2句话，具体可操作", "weakness_advice": "针对最弱领域(分数最低的分类)的提升建议，1-2句话，具体可操作"}}

注意：
- 建议要具体，不要空泛的"继续加油"，要指出具体可以做什么（如学习某个技术、做某类项目、考某个认证等）
- 提到具体的分类名称和分数
- 每条建议控制在 50 字以内
"""


async def _generate_skill_advice(
    db: AsyncSession,
    user_id: uuid.UUID,
    skills_section: dict[str, Any],
    scores: dict[str, dict],
    llm: BaseLLMProvider,
) -> None:
    """Generate strength/weakness advice via LLM and persist."""
    # Build category → avg score mapping
    category_scores: dict[str, float] = {}
    for category, items in skills_section.items():
        if not isinstance(items, list):
            continue
        child_scores = []
        for item in items:
            if isinstance(item, str) and item.strip():
                info = scores.get(item.strip(), {})
                child_scores.append(info.get("score", 5))
        if child_scores:
            category_scores[category] = round(sum(child_scores) / len(child_scores), 1)

    if len(category_scores) < 2:
        logger.info("Not enough categories for advice generation, skipping")
        return

    scores_text = "\n".join(f"- {name}: {avg} 分" for name, avg in category_scores.items())
    prompt = SKILL_ADVICE_PROMPT.format(category_scores=scores_text)

    try:
        response = await llm.chat(
            [{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        result = json.loads(text)
        strength = result.get("strength_advice", "")
        weakness = result.get("weakness_advice", "")

        if strength or weakness:
            advice_repo = SkillAdviceRepository(db)
            await advice_repo.upsert(user_id, strength, weakness)
            logger.info(f"Skill advice generated for user {user_id}")
    except Exception as e:
        logger.warning(f"Skill advice generation failed (non-fatal): {e}")


async def init_skill_tree_from_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
    parsed_data: dict[str, Any],
    llm: BaseLLMProvider | None = None,
) -> list[dict]:
    """Generate initial skill tree nodes from parsed resume data (source_type='resume_claimed').

    If llm is provided, uses LLM to score each skill 0-10. Otherwise defaults to 5.
    """
    repo = SkillTreeRepository(db)
    skills_section = parsed_data.get("skills", {})

    # Collect all skill names first for batch LLM scoring
    all_skill_names: list[str] = []
    for category, items in skills_section.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, str) and item.strip():
                all_skill_names.append(item.strip())

    # Also from projects
    for project in parsed_data.get("projects", []):
        for tech in project.get("tech_stack", []):
            if isinstance(tech, str) and tech.strip() and tech.strip() not in all_skill_names:
                all_skill_names.append(tech.strip())

    # Get LLM scores if provider available
    scores: dict[str, dict] = {}
    if llm and all_skill_names:
        scores = await _score_skills_with_llm(llm, parsed_data, all_skill_names)

    # Create category parents and child skills
    for category, items in skills_section.items():
        if not isinstance(items, list):
            continue

        # Calculate category average score from children
        child_scores = []
        for item in items:
            if isinstance(item, str) and item.strip():
                info = scores.get(item.strip(), {})
                child_scores.append(info.get("score", 5))
        avg_score = round(sum(child_scores) / len(child_scores)) if child_scores else 5

        parent = await repo.find_by_name(user_id, category)
        if not parent:
            parent = await repo.create(
                user_id=user_id,
                skill_name=category,
                source_type="resume_claimed",
                proficiency_score=avg_score,
            )

        for item in items:
            if isinstance(item, str) and item.strip():
                existing = await repo.find_by_name(user_id, item)
                if not existing:
                    info = scores.get(item.strip(), {})
                    await repo.create(
                        user_id=user_id,
                        skill_name=item,
                        parent_skill_id=parent.id,
                        source_type="resume_claimed",
                        proficiency_score=info.get("score", 5),
                        evaluation_comment=info.get("comment"),
                    )

    # Also extract skills from projects (no parent)
    for project in parsed_data.get("projects", []):
        for tech in project.get("tech_stack", []):
            if isinstance(tech, str) and tech.strip():
                existing = await repo.find_by_name(user_id, tech)
                if not existing:
                    info = scores.get(tech.strip(), {})
                    await repo.create(
                        user_id=user_id,
                        skill_name=tech,
                        source_type="resume_claimed",
                        proficiency_score=info.get("score", 5),
                        evaluation_comment=info.get("comment"),
                    )

    # Generate advice after all skills are created
    if llm:
        await _generate_skill_advice(db, user_id, skills_section, scores, llm)

    return [{"status": "ok"}]


async def rebuild_skill_tree(
    db: AsyncSession,
    user_id: uuid.UUID,
    parsed_data: dict[str, Any],
    llm: BaseLLMProvider | None = None,
) -> list[dict]:
    """Delete all existing skill nodes for the user and rebuild from resume data."""
    repo = SkillTreeRepository(db)
    deleted = await repo.delete_by_user(user_id)
    logger.info(f"Deleted {deleted} skill nodes for user {user_id}")
    return await init_skill_tree_from_resume(db, user_id, parsed_data, llm)


async def add_gap_skills_from_jd(
    db: AsyncSession,
    user_id: uuid.UUID,
    parsed_requirements: dict[str, Any],
) -> list[dict]:
    """Add inferred gap skill nodes based on JD requirements that aren't in the user's skill tree."""
    repo = SkillTreeRepository(db)
    existing_skills = await repo.get_by_user(user_id)
    existing_names = {s.skill_name.lower() for s in existing_skills}

    required = parsed_requirements.get("required_skills", [])
    preferred = parsed_requirements.get("preferred_skills", [])

    gaps_added = []
    for skill_name in required + preferred:
        if isinstance(skill_name, str) and skill_name.lower() not in existing_names:
            await repo.create(
                user_id=user_id,
                skill_name=skill_name,
                source_type="inferred_gap",
                proficiency_score=0,
                focus_status="active_learning",
            )
            gaps_added.append(skill_name)
            existing_names.add(skill_name.lower())

    return gaps_added
