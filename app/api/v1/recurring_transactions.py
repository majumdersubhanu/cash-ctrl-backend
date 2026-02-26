from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.recurring_transaction import (
    RecurringTransactionCreate,
    RecurringTransactionResponse,
)
from app.services.recurring_transaction_service import RecurringTransactionService


router = APIRouter(tags=["recurring"])


async def get_recurring_service() -> RecurringTransactionService:
    return RecurringTransactionService()


@router.post("/", response_model=RecurringTransactionResponse)
async def create_recurring_job(
    payload: RecurringTransactionCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: RecurringTransactionService = Depends(get_recurring_service),
):
    try:
        return await service.create_recurring(db=db, user_id=user.id, payload=payload)
    except Exception as e:
