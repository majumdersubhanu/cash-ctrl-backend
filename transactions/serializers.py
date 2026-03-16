from rest_framework import serializers
from .models import Category, Transaction

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'parent', 'name', 'type', 'icon', 'color', 'created_at')
        read_only_fields = ('id', 'created_at')

class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    account_name = serializers.ReadOnlyField(source='account.name')
    to_account_name = serializers.ReadOnlyField(source='to_account.name')

    class Meta:
        model = Transaction
        fields = (
            'id', 'account', 'account_name', 'to_account', 'to_account_name',
            'category', 'category_name', 'type', 'status', 'amount',
            'description', 'date', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'status', 'date', 'created_at', 'updated_at')
