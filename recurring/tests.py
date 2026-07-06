from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import BankAccount
from recurring.models import RecurringTransaction
from recurring.services import RecurringService

User = get_user_model()


class RecurringServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_recurring@example.com", password="password123"
        )
        self.account = BankAccount.objects.create(
            user=self.user,
            name="Test Account",
            balance=Decimal("1000.00"),
            bank_name="Test Bank",
            account_number="123456789",
        )

    @patch("django.utils.timezone.now")
    def test_process_recurring_daily(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime(2026, 7, 6, 12, 0, 0))

        rt = RecurringTransaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("50.00"),
            type="EXPENSE",
            description="Daily Expense",
            interval="DAILY",
            start_date=date(2026, 7, 5),
            next_execution=date(2026, 7, 6),
        )

        count = RecurringService.process_recurring()
        self.assertEqual(count, 1)
        self.assertEqual(str(rt), "Daily Expense (DAILY)")

        rt.refresh_from_db()
        self.assertEqual(rt.last_executed, date(2026, 7, 6))
        self.assertEqual(rt.next_execution, date(2026, 7, 7))

    @patch("django.utils.timezone.now")
    def test_process_recurring_weekly(self, mock_now):
        mock_now.return_value = timezone.make_aware(datetime(2026, 7, 6, 12, 0, 0))

        rt = RecurringTransaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("50.00"),
            type="EXPENSE",
            description="Weekly Expense",
            interval="WEEKLY",
            start_date=date(2026, 6, 29),
            next_execution=date(2026, 7, 6),
        )

        count = RecurringService.process_recurring()
        self.assertEqual(count, 1)

        rt.refresh_from_db()
        self.assertEqual(rt.last_executed, date(2026, 7, 6))
        self.assertEqual(rt.next_execution, date(2026, 7, 13))

    @patch("django.utils.timezone.now")
    def test_process_recurring_monthly(self, mock_now):
        # Month ending Jan 31st. Next execution should be Feb 28th (non-leap year 2025)
        mock_now.return_value = timezone.make_aware(datetime(2025, 1, 31, 12, 0, 0))

        rt = RecurringTransaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("100.00"),
            type="EXPENSE",
            description="Monthly Rent",
            interval="MONTHLY",
            start_date=date(2024, 12, 31),
            next_execution=date(2025, 1, 31),
        )

        count = RecurringService.process_recurring()
        self.assertEqual(count, 1)

        rt.refresh_from_db()
        self.assertEqual(rt.last_executed, date(2025, 1, 31))
        self.assertEqual(rt.next_execution, date(2025, 2, 28))

    @patch("django.utils.timezone.now")
    def test_process_recurring_yearly(self, mock_now):
        # Year ending on leap day Feb 29, 2024. Next execution should be Feb 28, 2025.
        mock_now.return_value = timezone.make_aware(datetime(2024, 2, 29, 12, 0, 0))

        rt = RecurringTransaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("200.00"),
            type="EXPENSE",
            description="Yearly Subscription",
            interval="YEARLY",
            start_date=date(2023, 2, 28),
            next_execution=date(2024, 2, 29),
        )

        count = RecurringService.process_recurring()
        self.assertEqual(count, 1)

        rt.refresh_from_db()
        self.assertEqual(rt.last_executed, date(2024, 2, 29))
        self.assertEqual(rt.next_execution, date(2025, 2, 28))

    @patch("django.utils.timezone.now")
    @patch("transactions.services.TransactionService.create_transaction")
    def test_process_recurring_exception(self, mock_create, mock_now):
        mock_now.return_value = timezone.make_aware(datetime(2026, 7, 6, 12, 0, 0))
        mock_create.side_effect = Exception("DB integrity failure")

        RecurringTransaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("50.00"),
            type="EXPENSE",
            description="Failing Expense",
            interval="DAILY",
            start_date=date(2026, 7, 5),
            next_execution=date(2026, 7, 6),
        )

        count = RecurringService.process_recurring()
        self.assertEqual(count, 0)
