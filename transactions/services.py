from django.db import transaction
from decimal import Decimal
from .models import Transaction, Category

class TransactionService:
    @staticmethod
    @transaction.atomic
    def create_transaction(user, account, type, amount, category=None, description="", status='POSTED'):
        """
        Creates a transaction and updates the account balance atomically.
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
            status=status
        )
        
        # Update account balance
        if status != 'CANCELLED' and status != 'DRAFT':
            if type == 'INCOME':
                account.balance += amount
            elif type == 'EXPENSE':
                account.balance -= amount
            account.save()
            
        return tx

    @staticmethod
    @transaction.atomic
    def transfer_money(user, from_account, to_account, amount, description=""):
        """
        Transfers money between accounts atomically.
        """
        amount = Decimal(str(amount))
        
        # Create the transfer record (Type: TRANSFER)
        # We record it on the 'from_account' and link 'to_account'
        tx = Transaction.objects.create(
            user=user,
            account=from_account,
            to_account=to_account,
            type='TRANSFER',
            amount=amount,
            description=description,
            status='POSTED'
        )
        
        # Update balances
        from_account.balance -= amount
        to_account.balance += amount
        
        from_account.save()
        to_account.save()
        
        return tx
