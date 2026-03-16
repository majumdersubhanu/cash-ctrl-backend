from django.test import TestCase
from django.contrib.auth import get_user_model
from lending.services import LoanService
from decimal import Decimal

User = get_user_model()

class LoanServiceTest(TestCase):
    def setUp(self):
        self.borrower = User.objects.create_user(email='borrower@test.com', password='password123')
        self.lender = User.objects.create_user(email='lender@test.com', password='password123')

    def test_create_loan_generates_installments(self):
        amount = Decimal('1200.00')
        duration = 12
        loan = LoanService.create_loan(
            borrower=self.borrower,
            amount=amount,
            interest_rate=Decimal('10.00'),
            duration_months=duration,
            lender=self.lender
        )
        
        self.assertEqual(loan.amount, amount)
        self.assertEqual(loan.installments.count(), duration)
        
        # Total interest = 1200 * 0.10 * 1 = 120
        # Total repayable = 1320
        # Monthly = 1320 / 12 = 110
        installment = loan.installments.first()
        self.assertEqual(installment.amount, Decimal('110.00'))
