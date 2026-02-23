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
                req.next_run_date = today + relativedelta(months=1)
            elif req.frequency == "Yearly":
                req.next_run_date = today + relativedelta(years=1)
        await db.commit()
        logger.info("Processed recurring transactions batch", extra={"count": len(reqs)})

@celery_app.task(name="process_recurring_transactions")
def process_recurring_transactions_task():
    logger.info("Executing scheduled task: process_recurring_transactions_task")
    asyncio.run(_process_recurring_transactions())

async def _check_overdue_loans():
    async with SessionLocal() as db:
        today = date.today()
        stmt = select(Loan).join(LoanAgreement).where(
            Loan.status == LoanStatus.ACTIVE,
            LoanAgreement.due_date < today
        )
        loans = (await db.execute(stmt)).scalars().all()
        for loan in loans:
            loan.status = LoanStatus.OVERDUE
            borrower_id = loan.contact_id if loan.is_lending else loan.user_id
            b_stmt = select(User).where(User.id == borrower_id)
            borrower = (await db.execute(b_stmt)).scalar_one_or_none()
            if borrower:
                borrower.vouch_score = max(0.0, float(borrower.vouch_score) - 10.0)
                # Notify User
                await notification_service.create_notification(
                    db=db,
                    user_id=borrower.id,
                    title="Loan Overdue",
                    message=f"Your loan for {loan.amount} is now overdue. Trust score penalized.",
                    notification_type=NotificationType.ALERT,
                    link=f"/p2p/loans/{loan.id}"
                )
                
        await db.commit()
        logger.info("Flagged overdue loans", extra={"count": len(loans)})

@celery_app.task(name="check_overdue_loans")
def check_overdue_loans_task():
    logger.info("Executing scheduled task: check_overdue_loans_task")
    asyncio.run(_check_overdue_loans())


