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

    async def get_cashflow_trends(
        self, db: AsyncSession, user_id: uuid.UUID, months: int = 6
    ):
        """Returns monthly income vs expenses over the last `months`."""
        start_date = datetime.now().date() - relativedelta(months=months)

        stmt = (
            select(
                extract("year", Transaction.transaction_date).label("year"),
                extract("month", Transaction.transaction_date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.type.in_([TransactionType.INCOME, TransactionType.EXPENSE]),
            )
            .group_by("year", "month", Transaction.type)
            .order_by("year", "month")
        )

        result = await db.execute(stmt)
        trends = {}
        for row in result.all():
            period = f"{int(row.year)}-{int(row.month):02d}"
            if period not in trends:
                trends[period] = {"income": 0.0, "expense": 0.0}

            if row.type == TransactionType.INCOME:
                trends[period]["income"] = float(row.total)
            else:
                trends[period]["expense"] = float(row.total)

        return trends

    async def get_safe_to_spend(self, db: AsyncSession, user_id: uuid.UUID) -> float:
        """
        Calculates 'Safe-to-Spend' balance:
        (Total Cash/Bank Account Balances) - (Upcoming Scheduled Expenses + Remaining Active Budgets)
        """
        now = datetime.now()

        # 1. Total liquid assets
        acc_stmt = select(func.sum(Account.balance)).where(
            Account.user_id == user_id, Account.type.in_(["BANK", "CASH", "WALLET"])
        )
        total_liquid = float((await db.execute(acc_stmt)).scalar() or 0.0)

        # 2. Remaining budgets for current month
        budget_stmt = select(Budget).where(Budget.user_id == user_id)
        budgets = (await db.execute(budget_stmt)).scalars().all()

        remaining_budget = 0.0
        for b in budgets:
            tx_stmt = select(func.sum(Transaction.amount)).where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                extract("month", Transaction.transaction_date) == now.month,
                extract("year", Transaction.transaction_date) == now.year,
            )
            if b.category_id:
                tx_stmt = tx_stmt.where(Transaction.category_id == b.category_id)

            spent = float((await db.execute(tx_stmt)).scalar() or 0.0)
            remaining_budget += max(0.0, float(b.amount) - spent)

        return total_liquid - remaining_budget

    async def detect_anomalies(self, db: AsyncSession, user_id: uuid.UUID):
        """
        Detect spending anomalies (transactions that are 200% higher than the avg for that category).
        """
        # Get avg per category
        avg_stmt = (
            select(
                Transaction.category_id, func.avg(Transaction.amount).label("avg_amt")
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
            )
            .group_by(Transaction.category_id)
        )
        avgs = {
            str(row.category_id): float(row.avg_amt)
            for row in (await db.execute(avg_stmt)).all()
        }

        # Get recent transactions (last 30 days)
        start_date = datetime.now().date() - relativedelta(days=30)
        recent_stmt = select(Transaction).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= start_date,
        )

        recent_txs = (await db.execute(recent_stmt)).scalars().all()

        anomalies = []
        for tx in recent_txs:
            if tx.category_id and str(tx.category_id) in avgs:
                avg = avgs[str(tx.category_id)]
                if avg > 0 and float(tx.amount) > (avg * 2):  # 2x the normal average
                    anomalies.append(
                        {
                            "id": str(tx.id),
                            "amount": float(tx.amount),
                            "description": tx.description,
                            "date": tx.transaction_date.isoformat(),
                            "normal_average": avg,
                        }
                    )

        return anomalies

    async def get_fire_insights(self, db: AsyncSession, user_id: uuid.UUID):
        """
        Calculates FIRE (Financial Independence, Retire Early) insights.
        Uses the 4% rule: FIRE Number = (Yearly Expenses) * 25.
        """
        now = datetime.now()
        
        # 1. Get average monthly income & expenses (last 6 months)
        start_date = now.date() - relativedelta(months=6)
        stmt = (
            select(Transaction.type, func.avg(Transaction.amount).label("avg_amt"))
            .where(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= start_date,
                Transaction.type.in_([TransactionType.INCOME, TransactionType.EXPENSE])
            )
            .group_by(Transaction.type)
        )
        results = (await db.execute(stmt)).all()
        
        avg_monthly_income = 0.0
        avg_monthly_expense = 0.0
        for row in results:
            if row.type == TransactionType.INCOME:
                avg_monthly_income = float(row.avg_amt or 0.0)
            else:
                avg_monthly_expense = float(row.avg_amt or 0.0)

        # 2. Get current net worth (liquid assets)
        acc_stmt = select(func.sum(Account.balance)).where(
            Account.user_id == user_id,
            Account.type.in_(["BANK", "CASH", "WALLET"])
        )
        current_net_worth = float((await db.execute(acc_stmt)).scalar() or 0.0)

        # 3. Calculations
        yearly_expense = avg_monthly_expense * 12
        fire_number = yearly_expense * 25
        
        monthly_savings = max(0.0, avg_monthly_income - avg_monthly_expense)
        
        remaining_gap = max(0.0, fire_number - current_net_worth)
        
        years_to_fire = None
        if monthly_savings > 0:
            years_to_fire = round(remaining_gap / (monthly_savings * 12), 1)

        return {
            "current_monthly_income": round(avg_monthly_income, 2),
            "current_monthly_expense": round(avg_monthly_expense, 2),
            "monthly_savings": round(monthly_savings, 2),
            "current_net_worth": round(current_net_worth, 2),
            "fire_number": round(fire_number, 2),
            "remaining_gap": round(remaining_gap, 2),
            "years_to_fire": years_to_fire,
            "status": "On Track" if monthly_savings > 0 else "Needs Adjustment"
        }
