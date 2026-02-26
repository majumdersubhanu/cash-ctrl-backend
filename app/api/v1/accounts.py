import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.services.account_service import AccountService

router = APIRouter(tags=["accounts"])


async def get_account_service() -> AccountService:
    return AccountService()


@router.post("/", response_model=AccountResponse)
async def create_account(
    payload: AccountCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AccountService = Depends(get_account_service),
):
    try:
        return await service.create_account(
            db=db,
            user_id=user.id,
            name=payload.name,
            account_type=payload.type,
            initial_balance=payload.balance,
            currency=payload.currency,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[AccountResponse])
async def list_accounts(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AccountService = Depends(get_account_service),
):
    return await service.get_accounts(db, user.id)

