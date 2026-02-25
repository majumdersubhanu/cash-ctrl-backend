import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class ConnectionRequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class ConnectionRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "connection_requests"

    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))

    status: Mapped[ConnectionRequestStatus] = mapped_column(
        SQLEnum(ConnectionRequestStatus), default=ConnectionRequestStatus.PENDING
    )

