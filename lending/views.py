from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Loan, Installment
from .serializers import LoanSerializer
from .services import LoanService
from accounts.models import Account

class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Users can see loans they've borrowed or lent
        return Loan.objects.filter(
            models.Q(borrower=self.request.user) | models.Q(lender=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        # We use the service to create the loan and its installments atomically
        loan = LoanService.create_loan(
            borrower=self.request.user,
            amount=serializer.validated_data['amount'],
            interest_rate=serializer.validated_data['interest_rate'],
            duration_months=serializer.validated_data['duration_months'],
            lender=serializer.validated_data.get('lender')
        )
        # Link to serializer so its data (including ID) is returned in the response
        serializer.instance = loan

    @action(detail=True, methods=['post'], url_path='pay/(?P<installment_id>[^/.]+)')
    def pay_installment(self, request, pk=None, installment_id=None):
        loan = self.get_object()
        try:
            installment = Installment.objects.get(id=installment_id, loan=loan)
        except Installment.DoesNotExist:
            return Response({"error": "Installment not found."}, status=status.HTTP_404_NOT_FOUND)

        account_id = request.data.get('account_id')
        if not account_id:
            return Response({"error": "account_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(id=account_id, user=request.user)
        except Account.DoesNotExist:
            return Response({"error": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            tx = LoanService.pay_installment(installment, account)
            return Response({"message": "Repayment successful", "transaction_id": tx.id})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
