from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SplitGroup, SplitExpense, SplitParticipation

User = get_user_model()


class SplitParticipationSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = SplitParticipation
        fields = ("id", "user", "user_email", "share_amount", "is_settled")


class SplitExpenseSerializer(serializers.ModelSerializer):
    participants = SplitParticipationSerializer(many=True, read_only=True)
    paid_by_email = serializers.ReadOnlyField(source="paid_by.email")

    class Meta:
        model = SplitExpense
        fields = (
            "id",
            "group",
            "paid_by",
            "paid_by_email",
            "amount",
            "currency",
            "description",
            "participants",
            "date",
        )
        read_only_fields = ("id", "date")


class SplitGroupSerializer(serializers.ModelSerializer):
    member_emails = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="email", source="members"
    )

    class Meta:
        model = SplitGroup
        fields = ("id", "name", "creator", "members", "member_emails", "created_at")
        read_only_fields = ("id", "creator", "created_at")
