import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction


class Tag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tags"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String)
    color: Mapped[Optional[str]] = mapped_column(String)

    user: Mapped["User"] = relationship(backref="tags")
    transactions: Mapped[List["Transaction"]] = relationship(
        secondary="transaction_tags", back_populates="tags"
    )
