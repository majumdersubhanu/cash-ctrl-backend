from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer
from .services import TransactionService
from integrations.scanner import ScannerService

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
    
    @action(detail=False, methods=['post'], url_path='scan-receipt')
    def scan_receipt(self, request):
        """
        Endpoint to upload a receipt image and get suggested transaction data.
        """
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save temporary file for processing
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        path = default_storage.save(f'tmp/scans/{image_file.name}', ContentFile(image_file.read()))
        
        # Process image
        result = ScannerService.scan_receipt(default_storage.path(path))
        
        # Cleanup
        default_storage.delete(path)
        
        return Response(result)

    def destroy(self, request, *args, **kwargs):
        # Need to handle balance reversal on delete
        return super().destroy(request, *args, **kwargs)
