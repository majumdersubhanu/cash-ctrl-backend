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

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AccountService = Depends(get_account_service),
):
    try:
        acct = await service.get_account(db, account_id)
        if acct.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        return acct
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: uuid.UUID,
    payload: AccountUpdate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AccountService = Depends(get_account_service),
):
    try:
        update_data = payload.model_dump(exclude_unset=True)
        return await service.update_account(db, account_id, user.id, **update_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{account_id}")
async def delete_account(
    account_id: uuid.UUID,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: AccountService = Depends(get_account_service),
):
    try:
        await service.delete_account(db, account_id, user.id)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
