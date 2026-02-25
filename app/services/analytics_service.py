import uuid

from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction
from app.models.account import Account
from app.models.budget import Budget
from app.utils.enums import TransactionType


class AnalyticsService:
    """Service providing intelligent financial insights, spending patterns, and net worth trends."""
