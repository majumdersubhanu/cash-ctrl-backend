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

