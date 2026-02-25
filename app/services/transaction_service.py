import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.utils.enums import TransactionType
from loguru import logger


class TransactionService:
    def __init__(self):
        self.tx_repo = TransactionRepository()
        self.account_repo = AccountRepository()

    async def create_transaction(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        account_id: uuid.UUID,
        category_id: Optional[uuid.UUID],
        amount: float,
        tx_type: TransactionType,
        note: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> Transaction:

