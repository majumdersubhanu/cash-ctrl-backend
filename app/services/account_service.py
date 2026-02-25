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
