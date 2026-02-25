from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class User(SQLAlchemyBaseUserTableUUID, Base, TimestampMixin):
    __tablename__ = "users"

    vouch_score: Mapped[float] = mapped_column(Float, default=0.0)
    totp_secret: Mapped[str | None] = mapped_column(default=None)
    is_mfa_enabled: Mapped[bool] = mapped_column(default=False)
