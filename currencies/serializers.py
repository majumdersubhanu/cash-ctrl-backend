from rest_framework import serializers
from .models import ExchangeRate

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ('id', 'base_currency', 'target_currency', 'rate', 'provider', 'last_updated')
        read_only_fields = ('id', 'last_updated')
