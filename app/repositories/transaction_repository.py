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
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        account_id: Optional[uuid.UUID] = None,
        category_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        keyword: Optional[str] = None,
        tags: Optional[list[str]] = None,
        sort_by: Optional[str] = "date",
        sort_order: Optional[str] = "desc",
    ) -> Sequence[Transaction]:

        stmt = select(Transaction).where(Transaction.user_id == user_id)

        if account_id:
            stmt = stmt.where(Transaction.account_id == account_id)

        if category_id:
            stmt = stmt.where(Transaction.category_id == category_id)

        if start_date:
            stmt = stmt.where(Transaction.transaction_date >= start_date)

        if end_date:
            stmt = stmt.where(Transaction.transaction_date <= end_date)

        if min_amount is not None:
            stmt = stmt.where(Transaction.amount >= min_amount)

        if max_amount is not None:
            stmt = stmt.where(Transaction.amount <= max_amount)

        if keyword:
            keyword_filter = f"%{keyword}%"
            stmt = stmt.where(
                (Transaction.description.ilike(keyword_filter))
                | (Transaction.note.ilike(keyword_filter))
            )

        if tags:
            from app.models.tag import Tag

