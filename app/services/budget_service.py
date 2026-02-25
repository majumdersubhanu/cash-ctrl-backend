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
