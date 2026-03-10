import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin
from app.utils.enums import AccountType

if TYPE_CHECKING:
    from app.models.user import User


class Account(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str]
    type: Mapped[AccountType]
    currency: Mapped[str] = mapped_column(String, default="INR")
    balance: Mapped[float] = mapped_column(default=0.0)

    credit_limit: Mapped[float] = mapped_column(Float, default=0.0)
    color: Mapped[Optional[str]] = mapped_column(String)
    icon: Mapped[Optional[str]] = mapped_column(String)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(backref="accounts")
