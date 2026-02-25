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

        # Verify receiver exists
        user_stmt = select(User).where(User.id == receiver_id)
        receiver = (await db.execute(user_stmt)).scalar_one_or_none()
        if not receiver:
            raise ContactNotFoundError("Receiver not found.")

        req = ConnectionRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status=ConnectionRequestStatus.PENDING,
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)

        # Notify receiver
        await self.notifications.create_notification(
            db=db,
            user_id=receiver_id,
            title="New Connection Request",
            message=f"Someone wants to connect with you on CashCtrl.",
            notification_type=NotificationType.INFO,
            link="/social/connections"
        )

        return req

    async def process_connection_request(
        self, db: AsyncSession, user_id: uuid.UUID, request_id: uuid.UUID, accept: bool
    ):
        from app.models.connection_request import (
            ConnectionRequest,
            ConnectionRequestStatus,
        )
        from app.models.user import User

        stmt = select(ConnectionRequest).where(
            ConnectionRequest.id == request_id,
            ConnectionRequest.receiver_id == user_id,
            ConnectionRequest.status == ConnectionRequestStatus.PENDING,
        )
        req = (await db.execute(stmt)).scalar_one_or_none()
        if not req:
            raise ValueError("Pending connection request not found.")

        if not accept:
            req.status = ConnectionRequestStatus.REJECTED
            await db.commit()
            return req

        # If accepted, map the reciprocal P2P Contacts implicitly.
        req.status = ConnectionRequestStatus.ACCEPTED

        sender = (
            await db.execute(select(User).where(User.id == req.sender_id))
        ).scalar_one()
        receiver = (
            await db.execute(select(User).where(User.id == req.receiver_id))
        ).scalar_one()

        contact_for_receiver = Contact(
            user_id=req.receiver_id,
            linked_user_id=req.sender_id,
            name=sender.email,  # Using email as default name.
            trust_score=sender.vouch_score,
            is_trusted=True,
        )

        contact_for_sender = Contact(
            user_id=req.sender_id,
            linked_user_id=req.receiver_id,
            name=receiver.email,
            trust_score=receiver.vouch_score,
            is_trusted=True,
        )
