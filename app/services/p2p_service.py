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
