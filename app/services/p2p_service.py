import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.models.contact import Contact
from app.models.loan import Loan, LoanAgreement, LoanInstallment
from app.utils.enums import LoanStatus, TransactionType
from app.services.transaction_service import TransactionService
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType
from loguru import logger


from app.core.exceptions import (
    ContactNotFoundError,
)

class P2PService:
    """Service for managing Peer-to-Peer lending lifecycle and social contacts."""
    
    def __init__(self):
        self.tx_service = TransactionService()
        self.notifications = NotificationService()

    async def create_contact(
        self, db: AsyncSession, user_id: uuid.UUID, payload
    ) -> Contact:
        contact = Contact(
            user_id=user_id,
            linked_user_id=payload.linked_user_id,
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
        )
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact

    async def get_user_contacts(
        self, db: AsyncSession, user_id: uuid.UUID
    ) -> Sequence[Contact]:
        stmt = select(Contact).where(Contact.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def send_connection_request(
        self, db: AsyncSession, sender_id: uuid.UUID, receiver_id: uuid.UUID
    ):
        """
        Sends a social connection request from one user to another.
        """
        from app.models.connection_request import (
            ConnectionRequest,
            ConnectionRequestStatus,
        )
        from app.models.user import User

