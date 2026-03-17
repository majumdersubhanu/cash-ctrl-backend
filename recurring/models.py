from django.db import models
from django.conf import settings
from transactions.models import Category, Transaction
import uuid


class RecurringTransaction(models.Model):
    INTERVAL_CHOICES = [
        ("DAILY", "Daily"),
        ("WEEKLY", "Weekly"),
        ("MONTHLY", "Monthly"),
        ("YEARLY", "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurring_transactions",
    )
    account = models.ForeignKey("accounts.Account", on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=Transaction.TransactionType.choices)
    description = models.CharField(max_length=255)

    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    start_date = models.DateField()
    last_executed = models.DateField(null=True, blank=True)
    next_execution = models.DateField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} ({self.interval})"
