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

        account = await self.account_repo.get_by_id(db, account_id)

        if not account:
            raise ValueError("Account not found")

        if tx_type == TransactionType.EXPENSE:
            if account.balance < amount:
                raise ValueError("Insufficient balance")

            account.balance -= amount

        elif tx_type == TransactionType.INCOME:
            account.balance += amount

        # Handle datetimes properly
        if timestamp is None:
            timestamp = datetime.now()

        tx = Transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            type=tx_type,
            note=note,
            transaction_date=timestamp.date(),
        )

        db.add(tx)
        await db.commit()
