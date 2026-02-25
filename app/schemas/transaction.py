from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.utils.enums import TransactionType


class TransactionCreate(BaseModel):
    account_id: UUID
    category_id: Optional[UUID] = None
    type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    note: Optional[str] = None


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    category_id: Optional[UUID] = None
    type: TransactionType
    amount: Decimal
    description: Optional[str] = None
    note: Optional[str] = None
    receipt_url: Optional[str] = None
    transaction_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransferCreate(BaseModel):
    from_account_id: UUID
    to_account_id: UUID
    amount: Decimal
    description: Optional[str] = None
    note: Optional[str] = None


class TransactionFilter(BaseModel):
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    keyword: Optional[str] = None
    tags: Optional[list[str]] = None
    sort_by: Optional[str] = "date"  # "date" or "amount"
    sort_order: Optional[str] = "desc"  # "asc" or "desc"


class BulkDeleteRequest(BaseModel):
    transaction_ids: list[UUID]
