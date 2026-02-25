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
