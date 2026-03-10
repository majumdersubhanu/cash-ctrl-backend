from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(tags=["categories"])


async def get_category_service() -> CategoryService:
    return CategoryService()


@router.post("/", response_model=CategoryResponse)
async def create_category(
    payload: CategoryCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: CategoryService = Depends(get_category_service),
):
    return await service.create_category(
        db=db, user_id=user.id, name=payload.name, category_type=payload.type, parent_id=payload.parent_id
    )


@router.get("/", response_model=list[CategoryResponse])
async def list_categories(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_user_categories(db, user.id)
