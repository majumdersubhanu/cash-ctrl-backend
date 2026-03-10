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


class ContactCreate(ContactBase):
    linked_user_id: Optional[UUID] = None


class ContactResponse(ContactBase):
    id: UUID
    linked_user_id: Optional[UUID] = None
    trust_score: float
    is_trusted: bool

    model_config = ConfigDict(from_attributes=True)


class LoanAgreementCreate(BaseModel):
    frequency: LoanRepaymentFrequency
    due_date: datetime.date


class LoanAgreementResponse(LoanAgreementCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class LoanCreate(BaseModel):
    contact_id: UUID
    is_lending: bool
    amount: Decimal
    currency: Optional[str] = "USD"
    interest_rate: Optional[Decimal] = None
    description: Optional[str] = None
    funding_account_id: Optional[UUID] = None

    # Optional agreement nested payload
    agreement: Optional[LoanAgreementCreate] = None


class LoanResponse(BaseModel):
    id: UUID
    contact_id: UUID
    is_lending: bool
    amount: Decimal
    currency: str
    interest_rate: Optional[Decimal]
    status: LoanStatus
    is_disputed: bool
    description: Optional[str]
    funding_account_id: Optional[UUID]
    created_at: datetime.datetime

    agreements: list[LoanAgreementResponse] = []

    model_config = ConfigDict(from_attributes=True)


class RepayLoanRequest(BaseModel):
    amount: Decimal
    account_id: UUID
    note: Optional[str] = None
