from rest_framework import serializers
from .models import Loan, Installment

class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = ('id', 'due_date', 'amount', 'status', 'paid_date', 'transaction')
        read_only_fields = ('id', 'paid_date', 'transaction')

class LoanSerializer(serializers.ModelSerializer):
    installments = InstallmentSerializer(many=True, read_only=True)
    borrower_email = serializers.ReadOnlyField(source='borrower.email')
    lender_email = serializers.ReadOnlyField(source='lender.email')

    class Meta:
        model = Loan
        fields = (
            'id', 'borrower', 'borrower_email', 'lender', 'lender_email',
            'amount', 'interest_rate', 'duration_months', 'status',
            'start_date', 'end_date', 'installments', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'start_date', 'end_date', 'created_at', 'updated_at')
