from enum import Enum


class AccountType(str, Enum):
    CASH = "CASH"
    BANK = "BANK"
    CARD = "CARD"
    WALLET = "WALLET"


class CategoryType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"


class LoanStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"
    DEFAULTED = "DEFAULTED"


class LoanRepaymentFrequency(str, Enum):
    LUMP_SUM = "LUMP_SUM"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
