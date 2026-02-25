import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.account_repository import AccountRepository


class AccountService:
    def __init__(self):
        self.repo = AccountRepository()

    async def create_account(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        name: str,
        account_type: str,
        initial_balance: float = 0,
        currency: str = "USD"
    ) -> Account:
        account = Account(
            name=name, type=account_type, balance=initial_balance, user_id=user_id, currency=currency
        )

        return await self.repo.create(db, account)

    async def get_accounts(self, db: AsyncSession, user_id: uuid.UUID):
        return await self.repo.get_user_accounts(db, user_id)

