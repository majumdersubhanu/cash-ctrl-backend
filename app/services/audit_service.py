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
