from django.db import transaction
from decimal import Decimal
from .models import Transaction


class TransactionService:
    """
    Orchestration layer for financial movements.
    
    Ensures that every transaction or transfer is processed atomically with its
    corresponding account balance updates.
    """
    @staticmethod
    @transaction.atomic
    def create_transaction(
        user, account, type, amount, category=None, description="", status="POSTED"
    ):
        """
        Executes a single-sided transaction (Income/Expense).
        
        Atomically records the entry and modifies the target account balance.
        """
        amount = Decimal(str(amount))

        # Create the transaction record
        tx = Transaction.objects.create(
            user=user,
            account=account,
            type=type,
            amount=amount,
            category=category,
            description=description,
            status=status,
        )

        # Update account balance
        if status != "CANCELLED" and status != "DRAFT":
            if type == "INCOME":
                account.balance += amount
            elif type == "EXPENSE":
                account.balance -= amount
            account.save()

        return tx

    @staticmethod
    @transaction.atomic
    def transfer_money(user, from_account, to_account, amount, description=""):
        """
        Synchronizes a double-sided transfer between two internal accounts.
        
        Maintains total system balance by decrementing the source and incrementing
        the destination atomically.
        """
        amount = Decimal(str(amount))

        # Create the transfer record (Type: TRANSFER)
        # We record it on the 'from_account' and link 'to_account'
        tx = Transaction.objects.create(
            user=user,
            account=from_account,
            to_account=to_account,
            type="TRANSFER",
            amount=amount,
            description=description,
            status="POSTED",
        )

        # Update balances
        from_account.balance -= amount
        to_account.balance += amount

        from_account.save()
        to_account.save()

        return tx
