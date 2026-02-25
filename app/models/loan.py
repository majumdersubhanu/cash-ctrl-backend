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
