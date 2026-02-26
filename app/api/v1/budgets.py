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
