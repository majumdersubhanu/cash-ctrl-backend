from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

class Loan(models.Model):
    class LoanStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACTIVE = 'ACTIVE', _('Active')
        FULLY_PAID = 'FULLY_PAID', _('Fully Paid')
        DEFAULTED = 'DEFAULTED', _('Defaulted')
        CANCELLED = 'CANCELLED', _('Cancelled')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans_given', null=True, blank=True)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans_taken')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate in percentage")
    duration_months = models.IntegerField()
    
    status = models.CharField(max_length=20, choices=LoanStatus.choices, default=LoanStatus.PENDING)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.id} - {self.borrower.email} ({self.amount})"

class Installment(models.Model):
    class InstallmentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')
        OVERDUE = 'OVERDUE', _('Overdue')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='installments')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=InstallmentStatus.choices, default=InstallmentStatus.PENDING)
    
    transaction = models.OneToOneField('transactions.Transaction', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Installment {self.loan.id} - {self.due_date} ({self.amount})"
