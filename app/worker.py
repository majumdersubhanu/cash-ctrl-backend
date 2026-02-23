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
