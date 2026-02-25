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
        await db.refresh(tx)

        logger.info("Transaction created", extra={"user_id": str(user_id), "transaction_id": str(tx.id), "amount": float(amount), "type": tx_type})
        return tx

    async def transfer_funds(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        from_account_id: uuid.UUID,
        to_account_id: uuid.UUID,
        amount: float,
        note: Optional[str] = None,
    ) -> tuple[Transaction, Transaction]:

        # Pull accounts
        from_acc = await self.account_repo.get_by_id(db, from_account_id)
        to_acc = await self.account_repo.get_by_id(db, to_account_id)

        if not from_acc or not to_acc:
            raise ValueError("Invalid account identifiers provided.")
        if from_acc.user_id != user_id or to_acc.user_id != user_id:
            raise ValueError("Accounts do not belong to the user.")
        if from_acc.balance < amount:
            raise ValueError(f"Insufficient funds in account {from_acc.name}.")

        from_acc.balance -= amount
        to_acc.balance += amount

        expense_tx = Transaction(
            user_id=user_id,
            account_id=from_account_id,
            amount=amount,
            type=TransactionType.TRANSFER,
            note=f"Transfer to {to_acc.name}: {note or ''}",
            transaction_date=datetime.now().date(),
        )
        income_tx = Transaction(
            user_id=user_id,
            account_id=to_account_id,
            amount=amount,
            type=TransactionType.TRANSFER,
            note=f"Transfer from {from_acc.name}: {note or ''}",
            transaction_date=datetime.now().date(),
        )
