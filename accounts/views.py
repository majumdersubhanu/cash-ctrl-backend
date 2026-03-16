from rest_framework import viewsets, permissions
from .models import Account
from .serializers import AccountSerializer

class AccountViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # Basic mapping based on type if needed, but for polymorphic models,
        # usually we might want specific serializers per subclass if creating.
        # For listing, we can use the base AccountSerializer.
        if self.action == 'create':
            # This is a bit simplified; real-world polymorphic DRF might use 
            # something like 'serializer_selection_field' or dedicated actions.
            return AccountSerializer
        return AccountSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
