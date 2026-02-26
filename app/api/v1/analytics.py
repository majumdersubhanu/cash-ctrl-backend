from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])


async def get_analytics_service() -> AnalyticsService:
    return AnalyticsService()


@router.get("/monthly-expense")
async def monthly_expense(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    total = await service.get_monthly_expense(db, user.id)
    return {"monthly_expense": total}


@router.get("/category-spending")
async def category_spending(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
