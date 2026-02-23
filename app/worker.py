import asyncio
from datetime import date
from dateutil.relativedelta import relativedelta

from celery import Celery
from celery.schedules import crontab
from loguru import logger
from sqlalchemy import select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.loan import Loan, LoanAgreement
from app.models.recurring_transaction import RecurringTransaction
from app.models.transaction import Transaction
from app.models.notification import NotificationType
from app.services.notification_service import NotificationService
from app.utils.enums import LoanStatus

notification_service = NotificationService()

celery_app = Celery(
    "cash_ctrl_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


async def _process_recurring_transactions():
    async with SessionLocal() as db:
        today = date.today()
        stmt = select(RecurringTransaction).where(
            RecurringTransaction.is_active.is_(True),
            RecurringTransaction.next_run <= today,
        )
        reqs = (await db.execute(stmt)).scalars().all()
        for req in reqs:
            tx = Transaction(
                user_id=req.user_id,
                account_id=req.account_id,
                category_id=req.category_id,
                amount=req.amount,
                type=req.type,
                transaction_date=today,
                note="Auto-generated from Recurring schedule"
            )
            db.add(tx)
            
            if req.frequency == "Daily":
                req.next_run_date = today + relativedelta(days=1)
            elif req.frequency == "Weekly":
                req.next_run_date = today + relativedelta(weeks=1)
            elif req.frequency == "Monthly":
