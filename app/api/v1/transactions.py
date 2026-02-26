from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.users import current_active_user
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionFilter,
    TransferCreate,
    BulkDeleteRequest,
)
from app.services.transaction_service import TransactionService

router = APIRouter(tags=["transactions"])


async def get_transaction_service() -> TransactionService:
    return TransactionService()


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    payload: TransactionCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return await service.create_transaction(
            db=db,
            user_id=user.id,
            account_id=payload.account_id,
            category_id=payload.category_id,
            amount=payload.amount,
            tx_type=payload.type,
            note=payload.note,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/filter", response_model=list[TransactionResponse])
async def filter_transactions(
    payload: TransactionFilter,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: TransactionService = Depends(get_transaction_service),
):
    return await service.tx_repo.filter_transactions(
        db=db,
        user_id=user.id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        min_amount=payload.min_amount,
        max_amount=payload.max_amount,
        keyword=payload.keyword,
        tags=payload.tags,
        sort_by=payload.sort_by,
        sort_order=payload.sort_order,
    )


@router.post("/transfer", response_model=list[TransactionResponse])
async def create_transfer(
    payload: TransferCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        expense, income = await service.transfer_funds(
            db=db,
            user_id=user.id,
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount=payload.amount,
            note=payload.note,
        )
        return [expense, income]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-delete")
async def bulk_delete_transactions(
    payload: BulkDeleteRequest,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: TransactionService = Depends(get_transaction_service),
):
    deleted_count = await service.bulk_delete_transactions(
        db=db, user_id=user.id, transaction_ids=payload.transaction_ids
    )
    return {"status": "ok", "deleted_count": deleted_count}
