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
    from app.models.category import Category


class Budget(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "budgets"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categories.id")
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    period: Mapped[str] = mapped_column(String)  # Monthly, Weekly, Yearly

    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)

    user: Mapped["User"] = relationship(backref="budgets")
    category: Mapped[Optional["Category"]] = relationship(backref="budgets")
