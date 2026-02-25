import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class Contact(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contacts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    # Optional map to an actual registered User ID inside the system
    linked_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)
    phone: Mapped[Optional[str]] = mapped_column(String)
    trust_score: Mapped[float] = mapped_column(Float, default=100.0)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(foreign_keys=[user_id], backref="contacts")
    linked_user: Mapped[Optional["User"]] = relationship(foreign_keys=[linked_user_id])
