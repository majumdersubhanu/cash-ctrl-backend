import io
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient

User = get_user_model()

CATEGORIES_URL = "/api/v1/transactions/categories/"
TRANSACTIONS_URL = "/api/v1/transactions/"
SCAN_RECEIPT_URL = "/api/v1/transactions/scan-receipt/"


def make_client(user=None):
    client = APIClient()
    if user:
        client.force_authenticate(user=user)
    return client


# ---------------------------------------------------------------------------
# CategoryViewSet
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoryViewSet:
    def test_list_requires_auth(self):
        response = make_client().get(CATEGORIES_URL)
        assert response.status_code == 401

    def test_list_returns_only_user_categories(self):
        user = baker.make("users.User")
        other = baker.make("users.User")
        baker.make("transactions.Category", user=user, name="Food", type="EXPENSE")
        baker.make("transactions.Category", user=other, name="Travel", type="EXPENSE")

        response = make_client(user).get(CATEGORIES_URL)
        assert response.status_code == 200
        names = [c["name"] for c in response.data]
        assert "Food" in names
        assert "Travel" not in names

    def test_create_category_sets_user(self):
        user = baker.make("users.User")
        data = {"name": "Groceries", "type": "EXPENSE"}
        response = make_client(user).post(CATEGORIES_URL, data, format="json")
        assert response.status_code == 201
        assert response.data["name"] == "Groceries"

    def test_retrieve_own_category(self):
        user = baker.make("users.User")
        cat = baker.make("transactions.Category", user=user, type="INCOME")
        response = make_client(user).get(f"{CATEGORIES_URL}{cat.id}/")
        assert response.status_code == 200
        assert response.data["id"] == str(cat.id)

    def test_retrieve_other_category_returns_404(self):
        user = baker.make("users.User")
        other = baker.make("users.User")
        cat = baker.make("transactions.Category", user=other, type="INCOME")
        response = make_client(user).get(f"{CATEGORIES_URL}{cat.id}/")
        assert response.status_code == 404

    def test_update_category_name(self):
        user = baker.make("users.User")
        cat = baker.make("transactions.Category", user=user, name="Old", type="EXPENSE")
        response = make_client(user).patch(
            f"{CATEGORIES_URL}{cat.id}/", {"name": "New"}, format="json"
        )
        assert response.status_code == 200
        assert response.data["name"] == "New"

    def test_delete_category(self):
        user = baker.make("users.User")
        cat = baker.make("transactions.Category", user=user, type="EXPENSE")
        response = make_client(user).delete(f"{CATEGORIES_URL}{cat.id}/")
        assert response.status_code == 204

    def test_create_subcategory_with_parent(self):
        user = baker.make("users.User")
        parent = baker.make("transactions.Category", user=user, type="EXPENSE")
        data = {"name": "Sub", "type": "EXPENSE", "parent": str(parent.id)}
        response = make_client(user).post(CATEGORIES_URL, data, format="json")
        assert response.status_code == 201
        assert str(response.data["parent"]) == str(parent.id)


# ---------------------------------------------------------------------------
# TransactionViewSet
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTransactionViewSet:
    def _make_account(self, user, balance=1000):
        return baker.make(
            "accounts.BankAccount",
            user=user,
            balance=balance,
            bank_name="Test Bank",
            account_number="12345",
        )

    def test_list_requires_auth(self):
        response = make_client().get(TRANSACTIONS_URL)
        assert response.status_code == 401

    def test_list_returns_only_user_transactions(self):
        user = baker.make("users.User")
        other = baker.make("users.User")
        acct = self._make_account(user)
        other_acct = self._make_account(other)
        tx_mine = baker.make(
            "transactions.Transaction",
            user=user,
            account=acct,
            type="INCOME",
            amount=100,
        )
        tx_other = baker.make(
            "transactions.Transaction",
            user=other,
            account=other_acct,
            type="INCOME",
            amount=200,
        )

        response = make_client(user).get(TRANSACTIONS_URL)
        assert response.status_code == 200
        ids = [t["id"] for t in response.data]
        assert str(tx_mine.id) in ids
        assert str(tx_other.id) not in ids

    def test_retrieve_own_transaction(self):
        user = baker.make("users.User")
        acct = self._make_account(user)
        tx = baker.make(
            "transactions.Transaction",
            user=user,
            account=acct,
            type="INCOME",
            amount=50,
        )
        response = make_client(user).get(f"{TRANSACTIONS_URL}{tx.id}/")
        assert response.status_code == 200

    def test_retrieve_other_transaction_returns_404(self):
        user = baker.make("users.User")
        other = baker.make("users.User")
        acct = self._make_account(other)
        tx = baker.make(
            "transactions.Transaction",
            user=other,
            account=acct,
            type="INCOME",
            amount=50,
        )
        response = make_client(user).get(f"{TRANSACTIONS_URL}{tx.id}/")
        assert response.status_code == 404

    def test_create_income_transaction(self):
        user = baker.make("users.User")
        acct = self._make_account(user)
        data = {
            "account": str(acct.id),
            "type": "INCOME",
            "amount": "500.00",
            "description": "Salary",
        }
        response = make_client(user).post(TRANSACTIONS_URL, data, format="json")
        assert response.status_code == 201

    def test_create_expense_transaction(self):
        user = baker.make("users.User")
        acct = self._make_account(user, balance=500)
        data = {
            "account": str(acct.id),
            "type": "EXPENSE",
            "amount": "100.00",
            "description": "Lunch",
        }
        response = make_client(user).post(TRANSACTIONS_URL, data, format="json")
        assert response.status_code == 201

    def test_create_transfer_transaction(self):
        user = baker.make("users.User")
        acct1 = self._make_account(user, balance=500)
        acct2 = self._make_account(user, balance=100)
        data = {
            "account": str(acct1.id),
            "to_account": str(acct2.id),
            "type": "TRANSFER",
            "amount": "200.00",
            "description": "Move funds",
        }
        response = make_client(user).post(TRANSACTIONS_URL, data, format="json")
        assert response.status_code == 201

    def test_delete_transaction(self):
        user = baker.make("users.User")
        acct = self._make_account(user)
        tx = baker.make(
            "transactions.Transaction",
            user=user,
            account=acct,
            type="INCOME",
            amount=50,
        )
        response = make_client(user).delete(f"{TRANSACTIONS_URL}{tx.id}/")
        assert response.status_code == 204

    def test_partial_update_description(self):
        user = baker.make("users.User")
        acct = self._make_account(user)
        tx = baker.make(
            "transactions.Transaction",
            user=user,
            account=acct,
            type="INCOME",
            amount=50,
            description="Old",
        )
        response = make_client(user).patch(
            f"{TRANSACTIONS_URL}{tx.id}/",
            {"description": "Updated"},
            format="json",
        )
        assert response.status_code == 200
        assert response.data["description"] == "Updated"


# ---------------------------------------------------------------------------
# TransactionViewSet.scan_receipt
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestScanReceiptAction:
    def test_scan_receipt_no_image_returns_400(self):
        user = baker.make("users.User")
        response = make_client(user).post(SCAN_RECEIPT_URL, {}, format="multipart")
        assert response.status_code == 400
        assert "No image provided" in str(response.data)

    def test_scan_receipt_with_image_calls_scanner(self):
        user = baker.make("users.User")
        fake_image = io.BytesIO(b"fake image data")
        fake_image.name = "receipt.jpg"

        mock_result = {
            "amount": Decimal("42.00"),
            "description": "Scanned Receipt: Gemini Mart",
            "raw_text": "Gemini Mart\nTotal 42.00",
        }

        with patch(
            "transactions.views.ScannerService.scan_receipt", return_value=mock_result
        ):
            response = make_client(user).post(
                SCAN_RECEIPT_URL, {"image": fake_image}, format="multipart"
            )
        assert response.status_code == 200
        assert response.data["description"] == "Scanned Receipt: Gemini Mart"

    def test_scan_receipt_requires_auth(self):
        response = make_client().post(SCAN_RECEIPT_URL, {}, format="multipart")
        assert response.status_code == 401
