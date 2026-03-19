from decimal import Decimal

import pytest

from accounts.models import WalletAccount
from lending.models import Installment
from lending.services import LoanService
from users.services import UserService


@pytest.fixture
def users_and_accounts():
    borrower = UserService.create_user(
        email="borrower@test.com", password="pwd", first_name="Bob"
    )
    lender = UserService.create_user(
        email="lender@test.com", password="pwd", first_name="Lenny"
    )

    # We create basic accounts for testing payment flows
    borrower_acc = WalletAccount.objects.create(
        user=borrower,
        name="Borrower Wallet",
        balance=Decimal("1500.00"),
        currency="USD",
        wallet_provider="Test",
    )
    lender_acc = WalletAccount.objects.create(
        user=lender,
        name="Lender Wallet",
        balance=Decimal("5000.00"),
        currency="USD",
        wallet_provider="Test",
    )

    return {
        "borrower": borrower,
        "lender": lender,
        "borrower_acc": borrower_acc,
        "lender_acc": lender_acc,
    }


@pytest.mark.django_db
class TestLoanService:
    def test_create_loan(self, users_and_accounts):
        """Test correct generation of a loan and its amortization schedule."""
        borrower = users_and_accounts["borrower"]
        lender = users_and_accounts["lender"]

        amount = Decimal("1200.00")
        interest_rate = Decimal("5.0")
        duration_months = 12

        loan = LoanService.create_loan(
            borrower=borrower,
            lender=lender,
            amount=amount,
            interest_rate=interest_rate,
            duration_months=duration_months,
        )

        assert loan.amount == amount
        assert loan.status == "ACTIVE"
        assert loan.borrower == borrower
        assert loan.lender == lender

        # Simple interest formula verification
        # Total Interest = (1200 * 5 * 12) / 1200 = 60
        # Total Repayable = 1260
        # Monthly Installment = 1260 / 12 = 105.00
        installments = Installment.objects.filter(loan=loan).order_by("due_date")

        assert installments.count() == duration_months
        for installment in installments:
            assert installment.amount == Decimal("105.00")
            assert installment.status == "PENDING"

    def test_pay_installment(self, users_and_accounts):
        """Test paying a specific installment successfully deducts funds and updates state."""
        borrower = users_and_accounts["borrower"]
        borrower_acc = users_and_accounts["borrower_acc"]

        loan = LoanService.create_loan(
            borrower=borrower,
            amount=Decimal("1200.00"),
            interest_rate=Decimal("5.0"),
            duration_months=12,
        )

        # Grab first installment
        installment = loan.installments.first()

        # Make payment
        tx = LoanService.pay_installment(installment=installment, account=borrower_acc)

        # Refresh from db
        borrower_acc.refresh_from_db()
        installment.refresh_from_db()
        loan.refresh_from_db()

        assert installment.status == "PAID"
        assert installment.transaction == tx

        # Check transaction creation
        assert tx.amount == installment.amount
        assert tx.type == "EXPENSE"
        assert "Loan Repayment" in tx.description
