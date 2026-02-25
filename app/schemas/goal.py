from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GoalCreate(BaseModel):
    account_id: Optional[UUID] = None
    name: str
    target_amount: Decimal
    deadline: Optional[date] = None


class GoalContribute(BaseModel):
    amount: Decimal


class GoalResponse(BaseModel):
    id: UUID
    account_id: Optional[UUID] = None
    name: str
    target_amount: Decimal
    current_amount: Decimal
    deadline: Optional[date] = None

    # Computed runtime
    percent_complete: Optional[float] = 0.0

    model_config = ConfigDict(from_attributes=True)
