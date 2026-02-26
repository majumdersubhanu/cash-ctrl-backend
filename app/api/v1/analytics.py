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
):
    return await service.get_category_spending(db, user.id)


@router.get("/cashflow-trends")
async def cashflow_trends(
    months: int = 6,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_cashflow_trends(db, user.id, months)


@router.get("/safe-to-spend")
async def safe_to_spend(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
    amount = await service.get_safe_to_spend(db, user.id)
    return {"safe_to_spend": amount}


@router.get("/anomalies")
async def get_anomalies(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AnalyticsService = Depends(get_analytics_service),
):
