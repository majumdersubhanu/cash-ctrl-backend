from rest_framework import viewsets, permissions
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer
from .services import TransactionService

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        # Use service to ensure atomic balance updates
        data = serializer.validated_data
        if data.get('type') == 'TRANSFER':
            TransactionService.transfer_money(
                user=self.request.user,
                from_account=data['account'],
                to_account=data['to_account'],
                amount=data['amount'],
                description=data.get('description', '')
            )
        else:
            TransactionService.create_transaction(
                user=self.request.user,
                account=data['account'],
                type=data['type'],
                amount=data['amount'],
                category=data.get('category'),
                description=data.get('description', '')
            )
    
    def destroy(self, request, *args, **kwargs):
        # Need to handle balance reversal on delete
        return super().destroy(request, *args, **kwargs)
