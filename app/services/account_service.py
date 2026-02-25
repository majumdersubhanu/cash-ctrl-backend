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

    async def get_account(self, db: AsyncSession, account_id: uuid.UUID) -> Account:
        account = await self.repo.get_by_id(db, account_id)
        if not account:
            raise ValueError("Account not found")
        return account

    async def update_account(self, db: AsyncSession, account_id: uuid.UUID, user_id: uuid.UUID, **kwargs) -> Account:
        account = await self.repo.get_by_id(db, account_id)
        if not account or account.user_id != user_id:
            raise ValueError("Account not found or access denied")
            
        return await self.repo.update(db, account, **kwargs)

    async def delete_account(self, db: AsyncSession, account_id: uuid.UUID, user_id: uuid.UUID) -> None:
        account = await self.repo.get_by_id(db, account_id)
