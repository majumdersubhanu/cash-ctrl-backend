from django.core.management.base import BaseCommand
from recurring.services import RecurringService
from analytics.models import Budget
from transactions.models import Transaction
from notifications.services import NotificationService
from django.db.models import Sum
from decimal import Decimal


class Command(BaseCommand):
    help = "Processes all recurring transactions and checks budget status"

    def handle(self, *args, **options):
        self.stdout.write("Starting system-wide processing...")

        # 1. Process Recurring Transactions
        processed_rt = RecurringService.process_recurring()
        self.stdout.write(
            self.style.SUCCESS(f"Processed {processed_rt} recurring transactions.")
        )

        # 2. Check Budgets
        self.stdout.write("Checking budgets...")
        budgets = Budget.objects.all()
        for budget in budgets:
            # Calculate current spend for the budget period
            # (Simplified for monthly budgets)
            start_date = budget.start_date
            spend = Transaction.objects.filter(
                user=budget.user,
                category=budget.category,
                type="EXPENSE",
                status="POSTED",
                date__gte=start_date,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

            NotificationService.alert_budget_limit(budget.user, budget, spend)

        self.stdout.write(self.style.SUCCESS("Budget checks completed."))
        self.stdout.write(
            self.style.SUCCESS("System processing finished successfully!")
        )
