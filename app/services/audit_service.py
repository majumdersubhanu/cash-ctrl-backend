import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.models.transaction import Transaction
from app.models.account import Account
from app.models.budget import Budget
from app.utils.enums import TransactionType

class HealthAuditService:
    """Service for performing comprehensive financial health audits for users."""

    async def perform_audit(self, db: AsyncSession, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Runs a full financial health audit.
        
        Args:
            db: Async database session.
            user_id: The ID of the user to audit.
            
        Returns:
            A dictionary containing health metrics.
        """
        now = datetime.now()
        
        # 1. Monthly Income & Expense
        income_stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            func.extract('month', Transaction.transaction_date) == now.month,
            func.extract('year', Transaction.transaction_date) == now.year
        )
        expense_stmt = select(func.sum(Transaction.amount)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            func.extract('month', Transaction.transaction_date) == now.month,
            func.extract('year', Transaction.transaction_date) == now.year
        )
        
        monthly_income = float((await db.execute(income_stmt)).scalar() or 0.0)
        monthly_expense = float((await db.execute(expense_stmt)).scalar() or 0.0)
        
        # 2. Savings Rate: (Income - Expense) / Income
