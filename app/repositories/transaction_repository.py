import uuid
from datetime import date
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.base_repository import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    async def get_user_transactions(
        self, db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> Sequence[Transaction]:

        stmt = (
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def filter_transactions(
