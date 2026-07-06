import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker
from accounts.models import Account, BankAccount, WalletAccount
from accounts.serializers import BankAccountSerializer, WalletAccountSerializer

User = get_user_model()


@pytest.mark.django_db
class TestAccountModels:
    def test_account_str(self):
        user = baker.make(User, username="test_account_owner")
        account = baker.make(Account, name="My Bank", user=user)
        assert str(account) == "My Bank (test_account_owner)"


@pytest.mark.django_db
class TestAccountSerializers:
    def test_bank_account_serializer(self):
        user = baker.make(User)
        bank_account = BankAccount.objects.create(
            user=user,
            name="Savings Account",
            balance=Decimal("1500.50"),
            currency="USD",
            bank_name="Test Bank",
            account_number="1234567890",
        )
        serializer = BankAccountSerializer(bank_account)
        assert serializer.data["bank_name"] == "Test Bank"
        assert serializer.data["account_number"] == "1234567890"

    def test_wallet_account_serializer(self):
        user = baker.make(User)
        wallet = WalletAccount.objects.create(
            user=user,
            name="Paypal Wallet",
            balance=Decimal("20.00"),
            currency="EUR",
            wallet_provider="Paypal",
        )
        serializer = WalletAccountSerializer(wallet)
        assert serializer.data["wallet_provider"] == "Paypal"


@pytest.mark.django_db
class TestAccountViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.user = baker.make(User)
        self.other_user = baker.make(User)
        self.client.force_authenticate(user=self.user)

    def test_list_accounts_only_shows_owned(self):
        baker.make(Account, user=self.user, name="User Account")
        baker.make(Account, user=self.other_user, name="Other Account")

        url = reverse("account-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        returned_names = [acc["name"] for acc in response.data]
        assert "User Account" in returned_names
        assert "Other Account" not in returned_names

    def test_retrieve_account_success(self):
        account = baker.make(Account, user=self.user, name="Savings")
        url = reverse("account-detail", kwargs={"pk": account.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Savings"

    def test_create_account(self):
        url = reverse("account-list")
        payload = {"name": "New Bank Account", "currency": "USD"}
        response = self.client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Bank Account"

        # Verify account created and associated with authenticated user
        assert Account.objects.filter(user=self.user, name="New Bank Account").exists()

    def test_update_account(self):
        account = baker.make(Account, user=self.user, name="Old Name")
        url = reverse("account-detail", kwargs={"pk": account.id})
        payload = {"name": "Updated Name", "currency": "GBP"}
        response = self.client.put(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"

    def test_delete_account(self):
        account = baker.make(Account, user=self.user)
        url = reverse("account-detail", kwargs={"pk": account.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Account.objects.filter(id=account.id).exists()
