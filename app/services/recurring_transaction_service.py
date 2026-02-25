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
