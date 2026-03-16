from django.utils import timezone
from datetime import timedelta
from .models import RecurringTransaction
from transactions.services import TransactionService
from transactions.models import Transaction
import logging

logger = logging.getLogger(__name__)

class RecurringService:
    @staticmethod
    def process_recurring():
        """
        System-wide processing of active recurring transactions due today.
        """
        today = timezone.now().date()
        due_transactions = RecurringTransaction.objects.filter(
            is_active=True,
            next_execution__lte=today
        )
        
        count = 0
        for rt in due_transactions:
            try:
                # Create the transaction
                TransactionService.create_transaction(
                    user=rt.user,
                    account=rt.account,
                    type=rt.type,
                    amount=rt.amount,
                    category=rt.category,
                    description=f"{rt.description} (Recurring)"
                )
                
                # Update next execution date
                rt.last_executed = today
                if rt.interval == 'DAILY':
                    rt.next_execution += timedelta(days=1)
                elif rt.interval == 'WEEKLY':
                    rt.next_execution += timedelta(weeks=1)
                elif rt.interval == 'MONTHLY':
                    # Simplified monthly jump
                    rt.next_execution += timedelta(days=30)
                elif rt.interval == 'YEARLY':
                    rt.next_execution += timedelta(days=365)
                
                rt.save()
                count += 1
            except Exception as e:
                logger.error(f"Failed to process recurring transaction {rt.id}: {str(e)}")
        
        return count
