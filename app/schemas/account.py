from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.utils.enums import AccountType


class AccountCreate(BaseModel):
    name: str
    type: AccountType
    currency: str = "INR"
    balance: float = 0.0


