from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetResponse
from app.services.budget_service import BudgetService


router = APIRouter(tags=["budgets"])


async def get_budget_service() -> BudgetService:
    return BudgetService()


@router.post("/", response_model=BudgetResponse)
async def create_budget(
    payload: BudgetCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: BudgetService = Depends(get_budget_service),
):
    try:
        return await service.create_budget(db=db, user_id=user.id, payload=payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[BudgetResponse])
async def list_budgets(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: BudgetService = Depends(get_budget_service),
):
    return await service.get_user_budgets_with_progress(db, user.id)
