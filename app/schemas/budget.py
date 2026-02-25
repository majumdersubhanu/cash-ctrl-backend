from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BudgetCreate(BaseModel):
    category_id: Optional[UUID] = None
    amount: Decimal
    period: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetResponse(BaseModel):
    id: UUID
    category_id: Optional[UUID] = None
    amount: Decimal
    period: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    # Computed runtime fields
    spent_amount: Optional[Decimal] = Decimal(0.0)
    remaining_amount: Optional[Decimal] = Decimal(0.0)
    is_overrun: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)
