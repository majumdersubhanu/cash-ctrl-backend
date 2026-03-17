from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Account
from .serializers import AccountSerializer

@extend_schema_view(
    list=extend_schema(summary="List user accounts", tags=["Accounts"]),
    retrieve=extend_schema(summary="Get specific account details", tags=["Accounts"]),
    create=extend_schema(summary="Create a new account", tags=["Accounts"]),
    update=extend_schema(summary="Update an entire account", tags=["Accounts"]),
    partial_update=extend_schema(summary="Partially update an account", tags=["Accounts"]),
    destroy=extend_schema(summary="Delete an account", tags=["Accounts"]),
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
