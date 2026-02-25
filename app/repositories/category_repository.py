import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.base_repository import BaseRepository
from app.utils.enums import CategoryType


class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

    async def get_user_categories(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> Sequence[Category]:
        stmt = select(Category).where(Category.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_type(
        self, db: AsyncSession, user_id: uuid.UUID, category_type: CategoryType
    ) -> Sequence[Category]:
        stmt = select(Category).where(
            Category.user_id == user_id, Category.type == category_type
        )
        result = await db.execute(stmt)
        return result.scalars().all()
