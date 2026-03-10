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
        stmt = (
            select(Transaction.transaction_date)
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
            )
            .order_by(Transaction.transaction_date.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        last_expense_date = result.scalar()

        if not last_expense_date:
            # If they've never ever had an expense, the streak is infinite. Default to 0?
            return 0

        today = datetime.now().date()
        delta = today - last_expense_date
        return max(
            0, delta.days - 1
        )  # Subtract 1 because if last expense was yesterday, streak is 0

    async def check_achievements(self, db: AsyncSession, user_id: uuid.UUID):
        """
        Checks for various static milestones based on ledger histories.
        """
        achievements = []

        streak = await self.get_no_spend_streak(db, user_id)
        if streak >= 7:
            achievements.append(
                {"name": "Frugal Week", "description": "7 day zero-spending streak!"}
            )
        if streak >= 30:
            achievements.append(
                {"name": "Zen Master", "description": "30 days zero-spending streak!"}
            )

        # Count total recorded transactions
        count_stmt = select(func.count(Transaction.id)).where(
            Transaction.user_id == user_id
        )
        total_txs = (await db.execute(count_stmt)).scalar() or 0

        if total_txs >= 100:
            achievements.append(
                {"name": "Centurion Tracker", "description": "Logged 100 transactions."}
            )
        if total_txs >= 1000:
            achievements.append(
                {
                    "name": "Grandmaster Ledger",
                    "description": "Logged over 1,000 transactions!",
                }
            )

        return achievements
