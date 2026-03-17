from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import BankAccount
from transactions.services import TransactionService
from decimal import Decimal

User = get_user_model()


class TransactionServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="password123"
        )
        self.account = BankAccount.objects.create(
            user=self.user,
            name="Test Account",
            balance=Decimal("1000.00"),
            bank_name="Test Bank",
            account_number="123456789",
        )

    def test_create_income_transaction(self):
        amount = Decimal("500.00")
        TransactionService.create_transaction(
            user=self.user,
            account=self.account,
            type="INCOME",
            amount=amount,
            description="Test Income",
            status="POSTED",
        )

        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("1500.00"))

    def test_create_expense_transaction(self):
        amount = Decimal("200.00")
        TransactionService.create_transaction(
            user=self.user,
            account=self.account,
            type="EXPENSE",
            amount=amount,
            description="Test Expense",
            status="POSTED",
        )

        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("800.00"))

    def test_create_transfer_transaction(self):
        target_account = BankAccount.objects.create(
            user=self.user,
            name="Target Account",
            balance=Decimal("100.00"),
            bank_name="Target Bank",
            account_number="987654321",
        )

        amount = Decimal("300.00")
        TransactionService.transfer_money(
            user=self.user,
            from_account=self.account,
            to_account=target_account,
            amount=amount,
            description="Test Transfer",
        )

        self.account.refresh_from_db()
        target_account.refresh_from_db()

        self.assertEqual(self.account.balance, Decimal("700.00"))
        self.assertEqual(target_account.balance, Decimal("400.00"))
