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
        elif split_type == 'percentage':
            # expects 'percentages': [{'user_id': id, 'percentage': 25}, ...]
            percentages_raw = request.data.get('percentages', [])
            user_percentages = []
            for item in percentages_raw:
                user = group.members.get(id=item['user_id'])
                user_percentages.append({'user': user, 'percentage': item['percentage']})
            participants_data = SplitService.calculate_percentage_split(amount, user_percentages)
        elif split_type == 'fixed':
            # expects 'shares': [{'user_id': id, 'amount': 50}, ...]
            shares_raw = request.data.get('shares', [])
            user_amounts = []
            for item in shares_raw:
                user = group.members.get(id=item['user_id'])
                user_amounts.append({'user': user, 'amount': item['amount']})
            participants_data = SplitService.calculate_fixed_amounts(amount, user_amounts)
        else:
            return Response({"error": f"Split type '{split_type}' not supported."}, status=status.HTTP_400_BAD_REQUEST)

        expense = SplitService.create_expense(
            group=group,
            paid_by=request.user,
            amount=amount,
            description=description,
            participants_data=participants_data
        )
        
        serializer = SplitExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
