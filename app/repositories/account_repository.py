import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.repositories.base_repository import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self):
        super().__init__(Account)

    async def get_user_accounts(
