import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.utils.enums import TransactionType


class GamificationService:
    async def get_no_spend_streak(self, db: AsyncSession, user_id: uuid.UUID) -> int:
        """
        Calculates the current active consecutive "no-spend" streak in days.
        A "no-spend" day has absolutely 0 Transactions evaluated as type EXPENSE.
        """
