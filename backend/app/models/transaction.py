import datetime
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Date, ForeignKey, Numeric, Text, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin
from app.utils.enums import TransactionType

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.category import Category
    from app.models.tag import Tag

transaction_tags = Table(
    "transaction_tags",
    Base.metadata,
    Column("transaction_id", ForeignKey("transactions.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Transaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"))
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categories.id")
    )

    type: Mapped[TransactionType]

    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    description: Mapped[Optional[str]] = mapped_column(Text)
    note: Mapped[Optional[str]] = mapped_column(Text)
    receipt_url: Mapped[Optional[str]] = mapped_column(String)

    transaction_date: Mapped[datetime.date] = mapped_column(Date)

    transfer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("transactions.id")
    )

    account: Mapped["Account"] = relationship(backref="transactions")
    category: Mapped[Optional["Category"]] = relationship(backref="transactions")
    tags: Mapped[List["Tag"]] = relationship(
        secondary=transaction_tags, back_populates="transactions"
    )
