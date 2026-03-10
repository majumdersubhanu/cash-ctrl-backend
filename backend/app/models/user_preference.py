import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserPreference(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    theme: Mapped[str] = mapped_column(String, default="light")
    default_currency: Mapped[str] = mapped_column(String, default="USD")
    dashboard_layout: Mapped[str] = mapped_column(String, default="default")

    user: Mapped["User"] = relationship(backref="preferences")
