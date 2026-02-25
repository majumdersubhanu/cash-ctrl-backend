from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.utils.enums import TransactionType


class RecurringTransactionCreate(BaseModel):
    account_id: UUID
    category_id: Optional[UUID] = None
    amount: Decimal
    type: TransactionType
    frequency: str
