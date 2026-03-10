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
    ) -> int:
        """
        Evaluates the existing recurring templates. If a template is past its next_run_date,
        it evaluates standard transaction logging through `TransactionService` and increments
        the next runtime based on the defined `frequency` (Daily, Weekly, Monthly, Yearly).
        """
        today = date.today()
        stmt = select(RecurringTransaction).where(
            RecurringTransaction.user_id == user_id,
            RecurringTransaction.is_active.is_(True),
            RecurringTransaction.next_run_date <= today,
        )

        result = await db.execute(stmt)
        due_jobs = result.scalars().all()

        processed_count = 0
        for job in due_jobs:
            try:
                await self.tx_service.create_transaction(
                    db=db,
                    user_id=user_id,
                    account_id=job.account_id,
                    category_id=job.category_id,
                    amount=float(job.amount),
                    tx_type=job.type,
                    note="Auto-generated from Recurring Tracker",
                    timestamp=None,  # defaults to now
                )

                # Increment date
                if job.frequency == "Daily":
                    job.next_run_date += relativedelta(days=1)
                elif job.frequency == "Weekly":
                    job.next_run_date += relativedelta(weeks=1)
                elif job.frequency == "Monthly":
                    job.next_run_date += relativedelta(months=1)
                elif job.frequency == "Yearly":
                    job.next_run_date += relativedelta(years=1)

                processed_count += 1
            except Exception as e:
                print(f"Failed to process job {job.id}: {e}")

        await db.commit()
        return processed_count
