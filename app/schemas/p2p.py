import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.utils.enums import LoanStatus, LoanRepaymentFrequency


class ContactBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


