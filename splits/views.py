from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import SplitGroupSerializer, SplitExpenseSerializer
from .services import SplitService

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary="List split groups",
        description="Retrieve all social groups where the user is either the creator or a participant. These groups serve as the shared context for multi-party expenses.",
        tags=["Splits"],
    ),
    retrieve=extend_schema(
        summary="Get specific group details",
        description="Access full metadata for a split group, including the member roster and historical group expenses.",
        tags=["Splits"],
    ),
    create=extend_schema(
        summary="Create a new split group",
        description="Establish a new social ledger for expense sharing. The creator is automatically added as the first member.",
        tags=["Splits"],
    ),
    update=extend_schema(
        summary="Update group metadata",
        description="Synchronize group attributes like the name. Typically used for group rename or structural updates.",
        tags=["Splits"],
    ),
    partial_update=extend_schema(
        summary="Partially update group info",
        description="Modify specific group fields without impacting the member list or expense history.",
        tags=["Splits"],
    ),
    destroy=extend_schema(
        summary="Disband a split group",
        description="Permanently archive or remove a group. Note: This may be restricted if there are unsettled expenses tethered to the group.",
        tags=["Splits"],
    ),
)
class SplitGroupViewSet(viewsets.ModelViewSet):
    """
    Orchestration center for social financial groups.
    """

    serializer_class = SplitGroupSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.request.user.split_groups.all()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["post"])
    def add_expense(self, request, pk=None):
        group = self.get_object()
        amount = request.data.get("amount")
        description = request.data.get("description")
        split_type = request.data.get("split_type", "equal")

        if not amount or not description:
            return Response(
                {"error": "amount and description are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if split_type == "equal":
            members = list(group.members.all())
            participants_data = SplitService.calculate_equal_split(amount, members)
        elif split_type == "percentage":
            # expects 'percentages': [{'user_id': id, 'percentage': 25}, ...]
            percentages_raw = request.data.get("percentages", [])
            user_percentages = []
            for item in percentages_raw:
                user = group.members.get(id=item["user_id"])
                user_percentages.append(
                    {"user": user, "percentage": item["percentage"]}
                )
            participants_data = SplitService.calculate_percentage_split(
                amount, user_percentages
            )
        elif split_type == "fixed":
            # expects 'shares': [{'user_id': id, 'amount': 50}, ...]
            shares_raw = request.data.get("shares", [])
            user_amounts = []
            for item in shares_raw:
                user = group.members.get(id=item["user_id"])
                user_amounts.append({"user": user, "amount": item["amount"]})
            participants_data = SplitService.calculate_fixed_amounts(
                amount, user_amounts
            )
        else:
            return Response(
                {"error": f"Split type '{split_type}' not supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expense = SplitService.create_expense(
            group=group,
            paid_by=request.user,
            amount=amount,
            description=description,
            participants_data=participants_data,
        )

        serializer = SplitExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
