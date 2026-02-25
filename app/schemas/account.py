from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.utils.enums import AccountType


class AccountCreate(BaseModel):
    name: str
    type: AccountType
    currency: str = "INR"
    balance: float = 0.0


class AccountUpdate(BaseModel):
    name: str | None = None
    type: AccountType | None = None
    currency: str | None = None
    balance: float | None = None
    is_archived: bool | None = None


class AccountResponse(BaseModel):
    id: UUID
    name: str
    type: AccountType
    currency: str
    balance: float
    is_archived: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
