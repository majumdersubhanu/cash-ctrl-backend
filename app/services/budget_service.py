import uuid
from datetime import datetime
from decimal import Decimal
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.transaction import Transaction
from app.utils.enums import TransactionType


class BudgetService:
    async def create_budget(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        payload,
    ) -> Budget:
        budget = Budget(
            user_id=user_id,
            category_id=payload.category_id,
            amount=payload.amount,
            period=payload.period,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
        return budget

    async def get_user_budgets_with_progress(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> Sequence[Budget]:
        stmt = select(Budget).where(Budget.user_id == user_id)
        result = await db.execute(stmt)
        budgets = result.scalars().all()

        for budget in budgets:
            # Calculate spent amount dynamically based on category targeting and active dates
            tx_stmt = select(
                func.coalesce(func.sum(Transaction.amount), Decimal(0.0))
            ).where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
            )

            if budget.category_id:
                tx_stmt = tx_stmt.where(Transaction.category_id == budget.category_id)

            if budget.start_date:
                tx_stmt = tx_stmt.where(
                    Transaction.transaction_date >= budget.start_date
                )

            if budget.end_date:
                tx_stmt = tx_stmt.where(Transaction.transaction_date <= budget.end_date)
            else:
