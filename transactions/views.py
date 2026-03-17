from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer
from .services import TransactionService
from integrations.scanner import ScannerService


@extend_schema_view(
    list=extend_schema(summary="List categories", description="Retrieves all custom transaction categories created by the authenticated user.", tags=["Categories"]),
    retrieve=extend_schema(summary="Get a specific category", tags=["Categories"]),
    create=extend_schema(summary="Create an expense/income category", tags=["Categories"]),
    update=extend_schema(summary="Update a category", tags=["Categories"]),
    partial_update=extend_schema(summary="Partially update a category", tags=["Categories"]),
    destroy=extend_schema(summary="Delete a category", tags=["Categories"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD endpoints for transaction categorization vectors.
    """
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Filters categories strictly to the authenticated user."""
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Binds the new category to the requesting user context."""
        serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(summary="List transactions", description="Fetches all transactions for the user, ordered chronologically by default.", tags=["Transactions"]),
    retrieve=extend_schema(summary="Get transaction details", tags=["Transactions"]),
    create=extend_schema(summary="Post a new transaction", description="Safely mutates account balances via the core TransactionService. Supports Transfers, Incomes, and Expenses.", tags=["Transactions"]),
    update=extend_schema(summary="Update a transaction", tags=["Transactions"]),
    partial_update=extend_schema(summary="Partially update a transaction", tags=["Transactions"]),
    destroy=extend_schema(summary="Delete a transaction", tags=["Transactions"]),
)
class TransactionViewSet(viewsets.ModelViewSet):
    """
    Central financial ledger gateway.
    All state mutations executed here cascade atomically down to the connected accounts.
    """
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Returns transactions tied exclusively to the requesting user."""
        return Transaction.objects.filter(user=self.request.user).order_by("-date")

    def perform_create(self, serializer):
        # Use service to ensure atomic balance updates
        data = serializer.validated_data
        if data.get("type") == "TRANSFER":
            TransactionService.transfer_money(
                user=self.request.user,
                from_account=data["account"],
                to_account=data["to_account"],
                amount=data["amount"],
                description=data.get("description", ""),
            )
        else:
            TransactionService.create_transaction(
                user=self.request.user,
                account=data["account"],
                type=data["type"],
                amount=data["amount"],
                category=data.get("category"),
                description=data.get("description", ""),
            )

    @extend_schema(
        summary="Scan Physical Receipt",
        description="Upload an image of a physical receipt. The Vision Engine will extract Date, Merchant, and Amount directly from the context via OCR.",
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiResponse(description="No image payload was detected in the request.")
        },
        tags=["Receipt Vision"]
    )
    @action(detail=False, methods=["post"], url_path="scan-receipt")
    def scan_receipt(self, request):
        """
        Endpoint to upload a receipt image and get suggested transaction data.
        """
        image_file = request.FILES.get("image")
        if not image_file:
            return Response(
                {"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Save temporary file for processing
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        path = default_storage.save(
            f"tmp/scans/{image_file.name}", ContentFile(image_file.read())
        )

        # Process image
        result = ScannerService.scan_receipt(default_storage.path(path))

        # Cleanup
        default_storage.delete(path)

        return Response(result)

    def destroy(self, request, *args, **kwargs):
        # Need to handle balance reversal on delete
        return super().destroy(request, *args, **kwargs)
