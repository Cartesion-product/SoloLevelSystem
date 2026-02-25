"""Interview domain repositories."""

import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interview.models import InterviewSession, Resume, TargetJob, User


class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID, **kwargs) -> Resume:
        resume = Resume(user_id=user_id, **kwargs)
        self.db.add(resume)
        await self.db.flush()
        await self.db.refresh(resume)
        return resume

    async def get_by_id(self, resume_id: uuid.UUID) -> Resume | None:
        result = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: uuid.UUID) -> list[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, resume_id: uuid.UUID, **kwargs) -> Resume | None:
        resume = await self.get_by_id(resume_id)
        if not resume:
            return None
        for key, value in kwargs.items():
            setattr(resume, key, value)
        await self.db.flush()
        await self.db.refresh(resume)
        return resume

    async def delete(self, resume_id: uuid.UUID) -> bool:
        resume = await self.get_by_id(resume_id)
        if not resume:
            return False
        await self.db.delete(resume)
        await self.db.flush()
        return True

    async def set_default(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume | None:
        # Clear current default
        await self.db.execute(
            update(Resume).where(Resume.user_id == user_id, Resume.is_default == True).values(is_default=False)
        )
        # Set new default
        return await self.update(resume_id, is_default=True)

    async def get_default(self, user_id: uuid.UUID) -> Resume | None:
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id, Resume.is_default == True)
        )
        return result.scalar_one_or_none()


class TargetJobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID, **kwargs) -> TargetJob:
        job = TargetJob(user_id=user_id, **kwargs)
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def get_by_id(self, job_id: uuid.UUID) -> TargetJob | None:
        result = await self.db.execute(select(TargetJob).where(TargetJob.id == job_id))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: uuid.UUID) -> list[TargetJob]:
        result = await self.db.execute(
            select(TargetJob).where(TargetJob.user_id == user_id).order_by(TargetJob.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, job_id: uuid.UUID, **kwargs) -> TargetJob | None:
        job = await self.get_by_id(job_id)
        if not job:
            return None
        for key, value in kwargs.items():
            setattr(job, key, value)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def delete(self, job_id: uuid.UUID) -> bool:
        job = await self.get_by_id(job_id)
        if not job:
            return False
        await self.db.delete(job)
        await self.db.flush()
        return True

    async def set_default(self, user_id: uuid.UUID, job_id: uuid.UUID) -> TargetJob | None:
        await self.db.execute(
            update(TargetJob).where(TargetJob.user_id == user_id, TargetJob.is_default == True).values(is_default=False)
        )
        job = await self.get_by_id(job_id)
        if job:
            job.is_default = True
            await self.db.flush()
            await self.db.refresh(job)
        return job

    async def get_default(self, user_id: uuid.UUID) -> TargetJob | None:
        result = await self.db.execute(
            select(TargetJob).where(TargetJob.user_id == user_id, TargetJob.is_default == True)
        )
        return result.scalar_one_or_none()


class InterviewSessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID, **kwargs) -> InterviewSession:
        session = InterviewSession(user_id=user_id, **kwargs)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: uuid.UUID) -> InterviewSession | None:
        result = await self.db.execute(
            select(InterviewSession).where(InterviewSession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: uuid.UUID, limit: int = 10) -> list[InterviewSession]:
        result = await self.db.execute(
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, session_id: uuid.UUID, **kwargs) -> InterviewSession | None:
        session = await self.get_by_id(session_id)
        if not session:
            return None
        for key, value in kwargs.items():
            setattr(session, key, value)
        await self.db.flush()
        await self.db.refresh(session)
        return session
