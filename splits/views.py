from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SplitGroup
from .serializers import SplitGroupSerializer, SplitExpenseSerializer
from .services import SplitService
from django.contrib.auth import get_user_model

User = get_user_model()

class SplitGroupViewSet(viewsets.ModelViewSet):
    serializer_class = SplitGroupSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.split_groups.all()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['post'])
    def add_expense(self, request, pk=None):
        group = self.get_object()
        amount = request.data.get('amount')
        description = request.data.get('description')
        split_type = request.data.get('split_type', 'equal')
        
        if not amount or not description:
            return Response({"error": "amount and description are required."}, status=status.HTTP_400_BAD_REQUEST)

        if split_type == 'equal':
            members = list(group.members.all())
            participants_data = SplitService.calculate_equal_split(amount, members)
        else:
            # For now, only equal split is implemented
            return Response({"error": "Only 'equal' split is currently supported."}, status=status.HTTP_400_BAD_REQUEST)

        expense = SplitService.create_expense(
            group=group,
            paid_by=request.user,
            amount=amount,
            description=description,
            participants_data=participants_data
        )
        
        serializer = SplitExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
