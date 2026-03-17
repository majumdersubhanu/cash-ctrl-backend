from django.db import models
from django.conf import settings
import uuid


class SplitGroup(models.Model):
    """
    Social grouping for expense sharing and collective debt management.

    Serves as the organizational container for multi-party financial splits.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_groups",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="split_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SplitExpense(models.Model):
    """
    Primary debit entry within a SplitGroup.

    Represents a master expenditure that will be proportionally allocated
    among group participants.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        SplitGroup, on_delete=models.CASCADE, related_name="expenses"
    )
    paid_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="paid_expenses"
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    description = models.CharField(max_length=255)

    date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} ({self.amount} {self.currency})"


class SplitParticipation(models.Model):
    """
    Proportional debt obligation belonging to a specific user for a given expense.

    Links individual users to their specific share of a SplitExpense.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(
        SplitExpense, on_delete=models.CASCADE, related_name="participants"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="participated_splits",
    )

    share_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_settled = models.BooleanField(default=False)

    def __str__(self):
        return (
            f"{self.user.email} owes {self.share_amount} for {self.expense.description}"
        )
