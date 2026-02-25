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


