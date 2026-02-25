"""Knowledge domain repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.knowledge.models import KnowledgeDocument


class KnowledgeDocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: uuid.UUID, **kwargs) -> KnowledgeDocument:
        doc = KnowledgeDocument(user_id=user_id, **kwargs)
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, doc_id: uuid.UUID) -> KnowledgeDocument | None:
        result = await self.db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == doc_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: uuid.UUID) -> list[KnowledgeDocument]:
        result = await self.db.execute(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.user_id == user_id)
            .order_by(KnowledgeDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, doc_id: uuid.UUID) -> bool:
        doc = await self.get_by_id(doc_id)
        if not doc:
            return False
        await self.db.delete(doc)
        await self.db.flush()
        return True
