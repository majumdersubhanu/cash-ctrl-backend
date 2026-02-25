import uuid
from datetime import date
from typing import Sequence
from dateutil.relativedelta import relativedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_transaction import RecurringTransaction
from app.services.transaction_service import TransactionService


class RecurringTransactionService:
    def __init__(self):
        self.tx_service = TransactionService()

    async def create_recurring(
        self, db: AsyncSession, user_id: uuid.UUID, payload
    ) -> RecurringTransaction:
        rt = RecurringTransaction(
            user_id=user_id,
            account_id=payload.account_id,
            category_id=payload.category_id,
            amount=payload.amount,
            type=payload.type,
            frequency=payload.frequency,
            next_run_date=payload.next_run_date,
            is_active=True,
        )
        db.add(rt)
        await db.commit()
        await db.refresh(rt)
        return rt

    async def get_user_recurring(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> Sequence[RecurringTransaction]:
        stmt = select(RecurringTransaction).where(
            RecurringTransaction.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def process_due_transactions(
        self, db: AsyncSession, user_id: uuid.UUID
