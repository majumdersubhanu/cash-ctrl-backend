from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions

from .models import Account
from .serializers import AccountSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List user accounts",
        description="Retrieve a comprehensive list of all financial accounts (Banks, Wallets, etc.) owned by the authenticated user. Useful for displaying a global balance overview.",
        tags=["Accounts"],
    ),
    retrieve=extend_schema(
        summary="Get specific account details",
        description="Enables detailed inspection of a singular account by its UUID. Returns the polymorphic data specific to the account type (e.g., bank_name for BankAccounts).",
        tags=["Accounts"],
    ),
    create=extend_schema(
        summary="Create a new account",
        description="Provision a new financial entity. The system automatically handles polymorphic instantiation and binds the account to the requesting user's identity.",
        tags=["Accounts"],
    ),
    update=extend_schema(
        summary="Update an entire account",
        description="Replace all fields of an existing account. Requires all mandatory fields. Use with caution as this affects the root financial entity.",
        tags=["Accounts"],
    ),
    partial_update=extend_schema(
        summary="Partially update an account",
        description="Safely mutate specific fields of an account (e.g., changing the name) without impacting other attributes or the current balance.",
        tags=["Accounts"],
    ),
    destroy=extend_schema(
        summary="Delete an account",
        description="Permanently remove an account from the system. Warning: This action is destructive and may fail if there are dependent transaction records.",
        tags=["Accounts"],
    ),
)
class AccountViewSet(viewsets.ModelViewSet):
    """
    Unified Command Center for User Financial Entities.

    Provides a high-performance interface for managing various account types
    (Banks, Wallets, etc.) through DRF's polymorphic view inheritance.
    Enforces strict ownership isolation and audit-ready data structures.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """
        Restrict the returned accounts to precisely those owned by the authenticated user.
        """
        return Account.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # Basic mapping based on type if needed, but for polymorphic models,
        # usually we might want specific serializers per subclass if creating.
        # For listing, we can use the base AccountSerializer.
        if self.action == "create":
            # This is a bit simplified; real-world polymorphic DRF might use
            # something like 'serializer_selection_field' or dedicated actions.
            return AccountSerializer
        return AccountSerializer

    def perform_create(self, serializer):
        """
        Automatically bind the newly created account to the authenticated user.
        """
        serializer.save(user=self.request.user)
