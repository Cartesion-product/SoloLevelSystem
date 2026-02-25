"""Interview domain services: resume parsing, JD parsing, session management."""

import json
from typing import Any

from app.infrastructure.llm_provider import BaseLLMProvider

# Resume parsing prompt templates per template type
RESUME_PARSE_TEMPLATES = {
    "ai_dev": {
        "focus": "AI frameworks, model experience, RAG practice, Agent orchestration",
        "schema": {
            "basic_info": {"name": "", "phone": "", "email": "", "education": [{"school": "", "degree": "", "major": "", "period": ""}]},
            "skills": {"languages": [], "frameworks": [], "databases": [], "tools": [], "domains": []},
            "projects": [{"name": "", "role": "", "period": "", "tech_stack": [], "description": "", "responsibilities": [], "achievements": [], "challenges": ""}],
            "work_experience": [{"company": "", "position": "", "period": "", "responsibilities": [], "achievements": []}],
        },
    },
    "backend": {
        "focus": "System design, databases, middleware, concurrency",
        "schema": {
            "basic_info": {"name": "", "phone": "", "email": "", "education": [{"school": "", "degree": "", "major": "", "period": ""}]},
            "skills": {"languages": [], "frameworks": [], "databases": [], "middleware": [], "tools": []},
            "projects": [{"name": "", "role": "", "period": "", "tech_stack": [], "description": "", "responsibilities": [], "achievements": [], "challenges": ""}],
            "work_experience": [{"company": "", "position": "", "period": "", "responsibilities": [], "achievements": []}],
        },
    },
    "fullstack": {
        "focus": "Frontend frameworks, API design, deployment, DevOps",
        "schema": {
            "basic_info": {"name": "", "phone": "", "email": "", "education": [{"school": "", "degree": "", "major": "", "period": ""}]},
            "skills": {"languages": [], "frontend_frameworks": [], "backend_frameworks": [], "databases": [], "tools": []},
            "projects": [{"name": "", "role": "", "period": "", "tech_stack": [], "description": "", "responsibilities": [], "achievements": [], "challenges": ""}],
            "work_experience": [{"company": "", "position": "", "period": "", "responsibilities": [], "achievements": []}],
        },
    },
    "data": {
        "focus": "ETL, data warehousing, SQL optimization, visualization",
        "schema": {
            "basic_info": {"name": "", "phone": "", "email": "", "education": [{"school": "", "degree": "", "major": "", "period": ""}]},
            "skills": {"languages": [], "frameworks": [], "databases": [], "etl_tools": [], "visualization": []},
            "projects": [{"name": "", "role": "", "period": "", "tech_stack": [], "description": "", "responsibilities": [], "achievements": [], "challenges": ""}],
            "work_experience": [{"company": "", "position": "", "period": "", "responsibilities": [], "achievements": []}],
        },
    },
    "generic": {
        "focus": "General skills, project experience, education background",
        "schema": {
            "basic_info": {"name": "", "phone": "", "email": "", "education": [{"school": "", "degree": "", "major": "", "period": ""}]},
            "skills": {"languages": [], "frameworks": [], "databases": [], "tools": []},
            "projects": [{"name": "", "role": "", "period": "", "tech_stack": [], "description": "", "responsibilities": [], "achievements": [], "challenges": ""}],
            "work_experience": [{"company": "", "position": "", "period": "", "responsibilities": [], "achievements": []}],
        },
    },
}


async def parse_resume_with_llm(
    raw_text: str,
    template_type: str,
    llm: BaseLLMProvider,
) -> dict[str, Any]:
    """Use LLM to structure raw resume text into the template schema."""
    template = RESUME_PARSE_TEMPLATES.get(template_type, RESUME_PARSE_TEMPLATES["generic"])

    prompt = f"""You are a resume parsing assistant. Parse the following resume text into the exact JSON structure provided.
Focus areas for this template ({template_type}): {template['focus']}

Output JSON schema (fill in values from the resume, use empty strings/lists for missing fields):
{json.dumps(template['schema'], ensure_ascii=False, indent=2)}

Resume text:
---
{raw_text}
---

Return ONLY valid JSON, no explanation."""

    response = await llm.chat([{"role": "user", "content": prompt}], temperature=0.1)

    # Extract JSON from response (handle markdown code blocks)
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    return json.loads(text)


async def parse_jd_with_llm(jd_text: str, llm: BaseLLMProvider) -> dict[str, Any]:
    """Use LLM to extract structured requirements from a job description."""
    prompt = f"""Analyze the following job description and extract structured requirements.

Return a JSON object with these fields:
{{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "experience_years": "e.g. 3-5",
  "key_responsibilities": ["resp1"],
  "technical_domains": ["domain1"]
}}

Job Description:
---
{jd_text}
---

Return ONLY valid JSON, no explanation."""

    response = await llm.chat([{"role": "user", "content": prompt}], temperature=0.1)

    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    return json.loads(text)
