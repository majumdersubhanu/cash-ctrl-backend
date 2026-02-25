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

