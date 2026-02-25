"""Resume API endpoints."""

import os
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.resumes import ResumeListResponse, ResumeResponse, ResumeUpdate
from app.config import get_settings
from app.core.logger import get_logger
from app.dependencies import get_current_user
from app.domain.interview.models import Resume, User
from app.domain.capability.service import init_skill_tree_from_resume
from app.domain.interview.repository import ResumeRepository
from app.domain.interview.service import parse_resume_with_llm
from app.infrastructure.database import async_session_factory, get_db
from app.infrastructure.file_parser import parse_file
from app.infrastructure.llm_provider import get_llm_provider

settings = get_settings()
logger = get_logger(__name__)
router = APIRouter(prefix="/resumes", tags=["resumes"])


def _to_response(r: Resume) -> ResumeResponse:
    return ResumeResponse(
        id=str(r.id),
        title=r.title,
        template_type=r.template_type,
        is_default=r.is_default,
        parsed_data=r.parsed_data or {},
        parsing_status=r.parsing_status or "completed",
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


async def _parse_resume_background(
    resume_id: uuid.UUID,
    user_id: uuid.UUID,
    raw_text: str,
    template_type: str,
):
    """Background task: LLM parse resume text → update DB → init skill tree."""
    try:
        llm = get_llm_provider()
        parsed_data = await parse_resume_with_llm(raw_text, template_type, llm)

        async with async_session_factory() as db:
            try:
                repo = ResumeRepository(db)
                await repo.update(resume_id, parsed_data=parsed_data, parsing_status="completed")

                # Init skill tree with LLM scoring
                try:
                    await init_skill_tree_from_resume(db, user_id, parsed_data, llm)
                    logger.info(f"Skill tree initialized from resume {resume_id}")
                except Exception as e:
                    logger.warning(f"Skill tree init failed (non-fatal): {e}")

                await db.commit()
            except Exception:
                await db.rollback()
                raise

        logger.info(f"Background parsing completed for resume {resume_id}")
    except Exception as e:
        logger.error(f"Background resume parsing failed for {resume_id}: {e}", exc_info=True)
        try:
            async with async_session_factory() as db:
                try:
                    repo = ResumeRepository(db)
                    await repo.update(resume_id, parsing_status="failed")
                    await db.commit()
                except Exception:
                    await db.rollback()
        except Exception as inner_e:
            logger.error(f"Failed to update parsing_status to failed: {inner_e}")


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(None),
    template_type: str = Form("generic"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a resume file and trigger background LLM parsing."""
    logger.info(f"Resume upload: file={file.filename}, template={template_type}, user={user.id}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    # Save file
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(file.filename or "file")[1]
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
    with open(file_path, "wb") as f:
        f.write(content)
    logger.debug(f"File saved: {file_path} ({len(content)} bytes)")

    # Parse file text (synchronous, fast)
    raw_text = parse_file(content, file.filename or "file.pdf")
    logger.debug(f"File parsed: {len(raw_text)} chars extracted")

    # Create resume record immediately with parsing status
    repo = ResumeRepository(db)
    resume = await repo.create(
        user_id=user.id,
        title=title or file.filename,
        template_type=template_type,
        raw_file_url=file_path,
        parsed_data={},
        parsing_status="parsing",
    )
    logger.info(f"Resume created: id={resume.id}, status=parsing")

    # Schedule background LLM parsing
    background_tasks.add_task(
        _parse_resume_background,
        resume.id,
        user.id,
        raw_text,
        template_type,
    )

    return _to_response(resume)


@router.get("", response_model=ResumeListResponse)
async def list_resumes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resumes = await repo.get_by_user(user.id)
    return ResumeListResponse(resumes=[_to_response(r) for r in resumes])


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(uuid.UUID(resume_id))
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    return _to_response(resume)


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: str,
    body: ResumeUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(uuid.UUID(resume_id))
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")

    updates = body.model_dump(exclude_none=True)
    resume = await repo.update(uuid.UUID(resume_id), **updates)
    return _to_response(resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(uuid.UUID(resume_id))
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    await repo.delete(uuid.UUID(resume_id))


@router.post("/{resume_id}/set-default", response_model=ResumeResponse)
async def set_default_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(uuid.UUID(resume_id))
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    resume = await repo.set_default(user.id, uuid.UUID(resume_id))
    return _to_response(resume)
