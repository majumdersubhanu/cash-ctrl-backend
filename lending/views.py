from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Loan, Installment
from .serializers import LoanSerializer
from .services import LoanService
from accounts.models import Account


@extend_schema_view(
    list=extend_schema(summary="List P2P Loans", description="Retrieve all loans where the authenticated user is either the lender or the borrower.", tags=["P2P Lending"]),
    retrieve=extend_schema(summary="Get Loan Details", tags=["P2P Lending"]),
    create=extend_schema(summary="Request/Create a Loan", description="Instantiates a new P2P computing contract. Automatically generates mathematically precise amortization schedules (installments) based on interest rate and duration.", tags=["P2P Lending"]),
    update=extend_schema(summary="Update Loan state", tags=["P2P Lending"]),
    partial_update=extend_schema(summary="Partially update Loan", tags=["P2P Lending"]),
    destroy=extend_schema(summary="Delete or Cancel a pending Loan", tags=["P2P Lending"]),
)
class LoanViewSet(viewsets.ModelViewSet):
    """
    Core gateway for the P2P Lending Engine.
    Handles loan instantiation, schedule generation, and installment lifecycle.
    """
    serializer_class = LoanSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        Secures the ledger: Users precisely see loans they've borrowed or equivalently lent.
        """
        return Loan.objects.filter(
            models.Q(borrower=self.request.user) | models.Q(lender=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        """
        Delegates loan execution to the LoanService to ensure atomic installment generation.
        """
        loan = LoanService.create_loan(
            borrower=self.request.user,
            amount=serializer.validated_data["amount"],
            interest_rate=serializer.validated_data["interest_rate"],
            duration_months=serializer.validated_data["duration_months"],
            lender=serializer.validated_data.get("lender"),
        )
        # Link to serializer so its data (including ID) is returned in the response
        serializer.instance = loan

    @extend_schema(
        summary="Pay Loan Installment",
        description="Processes a payment for a specific loan installment. Atomically transfers funds from the specified account to the lender, registers the transaction, and marks the installment as PAID.",
        parameters=[
            OpenApiParameter(name="installment_id", type=OpenApiTypes.UUID, location=OpenApiParameter.PATH, description="The unique ID of the installment being paid.")
        ],
        tags=["P2P Lending"]
    )
    @action(detail=True, methods=["post"], url_path="pay/(?P<installment_id>[^/.]+)")
    def pay_installment(self, request, pk=None, installment_id=None):
        """
        Facilitates the repayment of a singular loan installment via the Account balance.
        """
        loan = self.get_object()
        try:
            installment = Installment.objects.get(id=installment_id, loan=loan)
        except Installment.DoesNotExist:
            return Response(
                {"error": "Installment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        account_id = request.data.get("account_id")
        if not account_id:
            return Response(
                {"error": "account_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = Account.objects.get(id=account_id, user=request.user)
        except Account.DoesNotExist:
            return Response(
                {"error": "Account not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            tx = LoanService.pay_installment(installment, account)
            return Response(
                {"message": "Repayment successful", "transaction_id": tx.id}
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
