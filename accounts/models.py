import uuid

from django.conf import settings
from django.db import models
from polymorphic.models import PolymorphicModel


class Account(PolymorphicModel):
    """
    Base abstraction for all financial holding entities in the CashCtrl ecosystem.

    This model utilizes polymorphic inheritance to support diverse account types
    while maintaining a unified interface for transactions and balance tracking.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts"
    )
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class BankAccount(Account):
    """
    Represents a formal banking relationship with external institutional identifiers.
    """

    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)


class WalletAccount(Account):
    """
    Represents digital wallets or neo-banking credit lines.
    """

    wallet_provider = models.CharField(max_length=100)
