from app.db.base import Base
from app.db.session import engine

# Import all models here so they are registered with Base.metadata
from app.models.user import User
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.budget import Budget
from app.models.goal import Goal
from app.models.recurring_transaction import RecurringTransaction
from app.models.debt import Debt
from app.models.tag import Tag
from app.models.user_preference import UserPreference
from app.models.contact import Contact
from app.models.loan import Loan, LoanAgreement, LoanInstallment
from app.models.connection_request import ConnectionRequest
from app.models.notification import Notification

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
