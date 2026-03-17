from django.db import transaction
from django.utils import timezone
from audit.services import AuditService
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from .models import Loan, Installment
from transactions.services import TransactionService


class LoanService:
    @staticmethod
    @transaction.atomic
    def create_loan(borrower, amount, interest_rate, duration_months, lender=None):
        """
        Creates a loan and generates monthly installments.
        """
        amount = Decimal(str(amount))
        interest_rate = Decimal(str(interest_rate))

        loan = Loan.objects.create(
            borrower=borrower,
            lender=lender,
            amount=amount,
            interest_rate=interest_rate,
            duration_months=duration_months,
            status="ACTIVE",  # For simplicity, start as active if approved
            start_date=timezone.now().date(),
        )

        # Calculate monthly installment (Simple Interest for now)
        total_interest = (amount * interest_rate * Decimal(duration_months)) / (
            Decimal("100") * Decimal("12")
        )
        total_repayable = amount + total_interest
        monthly_amount = total_repayable / Decimal(duration_months)

        # Generate installments
        start_date = loan.start_date
        for i in range(1, duration_months + 1):
            due_date = start_date + relativedelta(months=i)
            Installment.objects.create(
                loan=loan, amount=monthly_amount, due_date=due_date, status="PENDING"
            )

        # Log loan creation
        AuditService.log_action(
            user=lender if lender else borrower,
            action="LOAN_CREATED",
            resource_type="Loan",
            resource_id=loan.id,
            changes={"amount": str(amount), "borrower": borrower.email},
        )

        return loan

    @staticmethod
    @transaction.atomic
    def pay_installment(installment, account):
        """
        Marks an installment as paid and creates a transaction.
        """
        if installment.status == "PAID":
            raise ValueError("Installment already paid.")

        # Create transaction for repayment
        # This is an EXPENSE for the borrower
        tx = TransactionService.create_transaction(
            user=installment.loan.borrower,
            account=account,
            type="EXPENSE",
            amount=installment.amount,
            description=f"Loan Repayment: {installment.loan.id} - {installment.due_date}",
            status="POSTED",
        )

        installment.status = "PAID"
        installment.paid_date = timezone.now().date()
        installment.transaction = tx
        installment.save()

        # Check if loan is fully paid
        if not installment.loan.installments.filter(
            status__in=["PENDING", "OVERDUE"]
        ).exists():
            installment.loan.status = "FULLY_PAID"
            installment.loan.save()

        return tx
