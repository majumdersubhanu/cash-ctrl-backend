import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin
from app.utils.enums import CategoryType

if TYPE_CHECKING:
    from app.models.user import User


class Category(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "categories"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str]
    type: Mapped[CategoryType]

    color: Mapped[Optional[str]] = mapped_column(String)
    icon: Mapped[Optional[str]] = mapped_column(String)

    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("categories.id"))

    user: Mapped["User"] = relationship(backref="categories")
    parent: Mapped[Optional["Category"]] = relationship(
        remote_side="Category.id", backref="children"
    )
