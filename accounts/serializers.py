from rest_framework import serializers
from .models import Account, BankAccount, WalletAccount

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'name', 'balance', 'currency', 'created_at', 'updated_at')
        read_only_fields = ('id', 'balance', 'created_at', 'updated_at')

class BankAccountSerializer(AccountSerializer):
    class Meta(AccountSerializer.Meta):
        model = BankAccount
        fields = AccountSerializer.Meta.fields + ('bank_name', 'account_number')

class WalletAccountSerializer(AccountSerializer):
    class Meta(AccountSerializer.Meta):
        model = WalletAccount
        fields = AccountSerializer.Meta.fields + ('wallet_provider',)
