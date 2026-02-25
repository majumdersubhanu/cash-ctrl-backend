import datetime
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import ForeignKey, String, Date, Numeric, Text, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin
from app.utils.enums import LoanStatus, LoanRepaymentFrequency

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.contact import Contact
    from app.models.account import Account


class Loan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "loans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id")
    )  # Extender of loan
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id"))

    # Whether the user is LENDING money to the contact, or BORROWING from them
    is_lending: Mapped[bool] = mapped_column(default=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String, default="USD")
    interest_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))

    status: Mapped[LoanStatus] = mapped_column(
        Enum(LoanStatus), default=LoanStatus.PENDING
    )
    is_disputed: Mapped[bool] = mapped_column(Boolean, default=False)

    description: Mapped[Optional[str]] = mapped_column(Text)
    attachment_url: Mapped[Optional[str]] = mapped_column(String)

    # Financial linkage
    funding_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("accounts.id")
    )

    user: Mapped["User"] = relationship(backref="loans")
    contact: Mapped["Contact"] = relationship(backref="loans")
    funding_account: Mapped[Optional["Account"]] = relationship()

    # Relationship to nested parts
    agreements: Mapped[List["LoanAgreement"]] = relationship(
        back_populates="loan", cascade="all, delete-orphan"
    )
    installments: Mapped[List["LoanInstallment"]] = relationship(
        back_populates="loan", cascade="all, delete-orphan"
    )


class LoanAgreement(Base, UUIDMixin, TimestampMixin):
    """
    Sub-model storing the negotiated terms of the loan lifecycle.
    """

    __tablename__ = "loan_agreements"

    loan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loans.id"))

    frequency: Mapped[LoanRepaymentFrequency] = mapped_column(
        Enum(LoanRepaymentFrequency)
    )
    due_date: Mapped[datetime.date] = mapped_column(Date)

    loan: Mapped["Loan"] = relationship(back_populates="agreements")


class LoanInstallment(Base, UUIDMixin, TimestampMixin):
    """
    Individual tracked breakdown segments of repayments.
    """

    __tablename__ = "loan_installments"

    loan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("loans.id"))

    amount_due: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0.0)

    due_date: Mapped[datetime.date] = mapped_column(Date)
    is_paid: Mapped[bool] = mapped_column(default=False)

    loan: Mapped["Loan"] = relationship(back_populates="installments")
