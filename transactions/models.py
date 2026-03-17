from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class Category(models.Model):
    """
    Hierarchical classification system for income and expense tracking.
    
    Supports nested subcategories and user-specific customizations (icons, colors).
    """
    class CategoryType(models.TextChoices):
        INCOME = "INCOME", _("Income")
        EXPENSE = "EXPENSE", _("Expense")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CategoryType.choices)
    icon = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ("user", "name", "parent")

    def __str__(self):
        return f"{self.name} ({self.type})"


class Transaction(models.Model):
    """
    Granular record of all financial movements within the ecosystem.
    
    Serves as the source of truth for account balances and analytics.
    Automatically linked to categories and accounts.
    """
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", _("Income")
        EXPENSE = "EXPENSE", _("Expense")
        TRANSFER = "TRANSFER", _("Transfer")

    class TransactionStatus(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        POSTED = "POSTED", _("Posted")
        CLEARED = "CLEARED", _("Cleared")
        CANCELLED = "CANCELLED", _("Cancelled")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    account = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, related_name="transactions"
    )
    to_account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_transfers",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(
        max_length=10,
        choices=TransactionStatus.choices,
        default=TransactionStatus.POSTED,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} - {self.amount} ({self.status})"
