from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient

User = get_user_model()

LOANS_URL = "/api/v1/lending/"


def make_client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user=user)
    return client


def make_account(user, balance=Decimal("10000.00")):
    return baker.make(
        "accounts.BankAccount",
        user=user,
        balance=balance,
        bank_name="Test Bank",
        account_number="99887766",
    )


@pytest.mark.django_db
class TestLoanViewSetCRUD:
    def test_list_requires_auth(self):
        response = make_client().get(LOANS_URL)
        assert response.status_code == 401

    def test_list_shows_only_user_loans(self):
        borrower = baker.make("users.User")
        other = baker.make("users.User")
        # Loan where user is borrower
        loan = baker.make(
            "lending.Loan",
            borrower=borrower,
            amount=1000,
            interest_rate=10,
            duration_months=3,
        )
        # Loan completely unrelated
        other_loan = baker.make(
            "lending.Loan",
            borrower=other,
            lender=other,
            amount=500,
            interest_rate=5,
            duration_months=2,
        )

        response = make_client(borrower).get(LOANS_URL)
        assert response.status_code == 200
        ids = [loan_item["id"] for loan_item in response.data]
        assert str(loan.id) in ids
        assert str(other_loan.id) not in ids

    def test_list_shows_loans_where_user_is_lender(self):
        lender = baker.make("users.User")
        borrower = baker.make("users.User")
        loan = baker.make(
            "lending.Loan",
            borrower=borrower,
            lender=lender,
            amount=2000,
            interest_rate=8,
            duration_months=6,
        )

        response = make_client(lender).get(LOANS_URL)
        assert response.status_code == 200
        ids = [loan_item["id"] for loan_item in response.data]
        assert str(loan.id) in ids

    def test_create_loan_generates_installments(self):
        borrower = baker.make("users.User")
        data = {
            "amount": "1200.00",
            "interest_rate": "10.00",
            "duration_months": 3,
        }
        response = make_client(borrower).post(LOANS_URL, data, format="json")
        assert response.status_code == 201
        assert len(response.data["installments"]) == 3

    def test_create_loan_with_lender(self):
        borrower = baker.make("users.User")
        lender = baker.make("users.User")
        data = {
            "amount": "5000.00",
            "interest_rate": "5.00",
            "duration_months": 12,
            "lender": str(lender.id),
        }
        response = make_client(borrower).post(LOANS_URL, data, format="json")
        assert response.status_code == 201
        assert response.data["borrower_email"] == borrower.email

    def test_retrieve_own_loan(self):
        borrower = baker.make("users.User")
        loan = baker.make(
            "lending.Loan",
            borrower=borrower,
            amount=1000,
            interest_rate=10,
            duration_months=6,
        )

        response = make_client(borrower).get(f"{LOANS_URL}{loan.id}/")
        assert response.status_code == 200
        assert response.data["id"] == str(loan.id)

    def test_retrieve_unrelated_loan_returns_404(self):
        user = baker.make("users.User")
        other = baker.make("users.User")
        loan = baker.make(
            "lending.Loan",
            borrower=other,
            amount=100,
            interest_rate=5,
            duration_months=1,
        )

        response = make_client(user).get(f"{LOANS_URL}{loan.id}/")
        assert response.status_code == 404

    def test_delete_loan(self):
        borrower = baker.make("users.User")
        loan = baker.make(
            "lending.Loan",
            borrower=borrower,
            amount=100,
            interest_rate=5,
            duration_months=1,
        )
        response = make_client(borrower).delete(f"{LOANS_URL}{loan.id}/")
        assert response.status_code == 204


@pytest.mark.django_db
class TestPayInstallmentAction:
    def test_pay_installment_success(self):
        borrower = baker.make("users.User")
        account = make_account(borrower, balance=Decimal("5000.00"))

        # Create a real loan via the service so installments are properly generated
        from lending.services import LoanService

        loan = LoanService.create_loan(
            borrower=borrower,
            amount=Decimal("300.00"),
            interest_rate=Decimal("10.00"),
            duration_months=3,
        )
        installment = loan.installments.filter(status="PENDING").first()

        url = f"{LOANS_URL}{loan.id}/pay/{installment.id}/"
        response = make_client(borrower).post(
            url, {"account_id": str(account.id)}, format="json"
        )
        assert response.status_code == 200
        assert "transaction_id" in response.data

    def test_pay_installment_no_account_id_returns_400(self):
        borrower = baker.make("users.User")
        from lending.services import LoanService

        loan = LoanService.create_loan(
            borrower=borrower,
            amount=Decimal("300.00"),
            interest_rate=Decimal("10.00"),
            duration_months=3,
        )
        installment = loan.installments.first()

        url = f"{LOANS_URL}{loan.id}/pay/{installment.id}/"
        response = make_client(borrower).post(url, {}, format="json")
        assert response.status_code == 400
        assert "account_id" in str(response.data)

    def test_pay_installment_invalid_account_returns_404(self):
        borrower = baker.make("users.User")
        from lending.services import LoanService

        loan = LoanService.create_loan(
            borrower=borrower,
            amount=Decimal("300.00"),
            interest_rate=Decimal("10.00"),
            duration_months=3,
        )
        installment = loan.installments.first()

        url = f"{LOANS_URL}{loan.id}/pay/{installment.id}/"
        response = make_client(borrower).post(
            url, {"account_id": "00000000-0000-0000-0000-000000000000"}, format="json"
        )
        assert response.status_code == 404

    def test_pay_nonexistent_installment_returns_404(self):
        borrower = baker.make("users.User")
        account = make_account(borrower)
        from lending.services import LoanService

        loan = LoanService.create_loan(
            borrower=borrower,
            amount=Decimal("300.00"),
            interest_rate=Decimal("10.00"),
            duration_months=3,
        )

        fake_installment_id = "00000000-0000-0000-0000-111111111111"
        url = f"{LOANS_URL}{loan.id}/pay/{fake_installment_id}/"
        response = make_client(borrower).post(
            url, {"account_id": str(account.id)}, format="json"
        )
        assert response.status_code == 404

    def test_pay_already_paid_installment_returns_400(self):
        borrower = baker.make("users.User")
        account = make_account(borrower, balance=Decimal("10000.00"))
        from lending.services import LoanService

        loan = LoanService.create_loan(
            borrower=borrower,
            amount=Decimal("300.00"),
            interest_rate=Decimal("10.00"),
            duration_months=3,
        )
        installment = loan.installments.first()

        url = f"{LOANS_URL}{loan.id}/pay/{installment.id}/"
        client = make_client(borrower)
        # First payment
        client.post(url, {"account_id": str(account.id)}, format="json")
        # Second payment attempt
        response = client.post(url, {"account_id": str(account.id)}, format="json")
        assert response.status_code == 400
