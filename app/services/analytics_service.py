import uuid

from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.account import Account
from app.models.budget import Budget
from app.utils.enums import TransactionType


class AnalyticsService:
    """Service providing intelligent financial insights, spending patterns, and net worth trends."""

    async def get_monthly_expense(self, db: AsyncSession, user_id: uuid.UUID) -> float:
        """Calculates total expense for the current month."""
        now = datetime.now()
        stmt = select(func.sum(Transaction.amount).label("total")).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            extract("month", Transaction.transaction_date) == now.month,
            extract("year", Transaction.transaction_date) == now.year,
        )
        result = await db.execute(stmt)
        return float(result.scalar() or 0.0)

    async def get_category_spending(self, db: AsyncSession, user_id: uuid.UUID):
        now = datetime.now()
        stmt = (
            select(Transaction.category_id, func.sum(Transaction.amount).label("total"))
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                extract("month", Transaction.transaction_date) == now.month,
                extract("year", Transaction.transaction_date) == now.year,
            )
            .group_by(Transaction.category_id)
        )
        result = await db.execute(stmt)
        return [
            {"category_id": str(row.category_id), "total": float(row.total)}
            for row in result.all()
        ]
