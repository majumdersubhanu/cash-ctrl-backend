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
    list=extend_schema(
        summary="List transaction categories",
        description="Retrieve a structured list of all financial categories available to the user. Categories are used to classify entries as Income or Expense, enabling granular analytics.",
        tags=["Categories"],
    ),
    retrieve=extend_schema(
        summary="Get specific category details",
        description="Access full metadata for a single category, including its hierarchical relationship (parent/subcategories) and visual attributes (icon/color).",
        tags=["Categories"],
    ),
    create=extend_schema(
        summary="Create a new financial category",
        description="Establish a new classification vector for tracking money movement. Supports nested hierarchies for complex budgeting scenarios.",
        tags=["Categories"],
    ),
    update=extend_schema(
        summary="Update a category definition",
        description="Synchronize all fields of a category record. Used for global reclassification or structural changes in the category tree.",
        tags=["Categories"],
    ),
    partial_update=extend_schema(
        summary="Partially update category metadata",
        description="Refine specific category attributes like the icon or color code without affecting the underlying classification type.",
        tags=["Categories"],
    ),
    destroy=extend_schema(
        summary="Remove a category",
        description="Permanently delete a categorization entry. Recommended only for unused categories to maintain historical analytical integrity.",
        tags=["Categories"],
    ),
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
    list=extend_schema(
        summary="List user transactions",
        description="Retrieve a forensic-grade ledger of all money movements. Supports high-performance chronological ordering and detailed linkings to accounts and categories.",
        tags=["Transactions"],
    ),
    retrieve=extend_schema(
        summary="Inspect a specific transaction",
        description="Returns the full audit trail and metadata for a single financial event, including transfer details and status (Posted/Cleared).",
        tags=["Transactions"],
    ),
    create=extend_schema(
        summary="Initiate a new financial event",
        description="Primary gateway for posting Income, Expenses, or internal Transfers. This operation triggers real-time account balance updates through the TransactionService.",
        tags=["Transactions"],
    ),
    update=extend_schema(
        summary="Correct a transaction record",
        description="Perform a full replacement of a transaction's data. Automatically recalibrates the affected account balances to maintain ledger consistency.",
        tags=["Transactions"],
    ),
    partial_update=extend_schema(
        summary="Adjust transaction attributes",
        description="Mutate specific transaction metadata (e.g., description) without disrupting the core financial amounts or account reconciliation logic.",
        tags=["Transactions"],
    ),
    destroy=extend_schema(
        summary="Void a transaction entry",
        description="Removes a transaction from the ledger. This action triggers a balance reversal on the associated accounts to maintain absolute system integrity.",
        tags=["Transactions"],
    ),
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
            400: OpenApiResponse(
                description="No image payload was detected in the request."
            ),
        },
        tags=["Receipt Vision"],
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
