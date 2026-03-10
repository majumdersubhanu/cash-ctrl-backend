import datetime
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Debt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "debts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)  # Owe, Owed
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    user: Mapped["User"] = relationship(backref="debts")
