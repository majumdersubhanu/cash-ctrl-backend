import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.utils.enums import CategoryType


class CategoryService:
    def __init__(self):
        self.repo = CategoryRepository()

    async def create_category(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        category_type: CategoryType,
        parent_id: uuid.UUID | None = None,
    ) -> Category:
        category = Category(name=name, type=category_type, user_id=user_id, parent_id=parent_id)

        return await self.repo.create(db, category)

    async def get_user_categories(self, db: AsyncSession, user_id: uuid.UUID):
        return await self.repo.get_user_categories(db, user_id)

    async def get_categories_by_type(
        self, db: AsyncSession, user_id: uuid.UUID, category_type: CategoryType
    ):
        return await self.repo.get_by_type(db, user_id, category_type)
