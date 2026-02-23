from enum import Enum


class AccountType(str, Enum):
    CASH = "CASH"
    BANK = "BANK"
    CARD = "CARD"
    WALLET = "WALLET"


class CategoryType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


