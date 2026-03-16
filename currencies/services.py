from decimal import Decimal
from .models import ExchangeRate

class CurrencyService:
    @staticmethod
    def convert(amount, from_currency, to_currency):
        """
        Converts an amount from one currency to another using stored exchange rates.
        """
        if from_currency == to_currency:
            return Decimal(str(amount))

        rate = ExchangeRate.get_rate(from_currency, to_currency)
        if rate is None:
            raise ValueError(f"Exchange rate not found for {from_currency} to {to_currency}")
            
        return Decimal(str(amount)) * Decimal(str(rate))

    @staticmethod
    def update_rate(base_currency, target_currency, rate, provider='manual'):
        """
        Updates or creates an exchange rate.
        """
        obj, created = ExchangeRate.objects.update_or_create(
            base_currency=base_currency,
            target_currency=target_currency,
            defaults={'rate': Decimal(str(rate)), 'provider': provider}
        )
        return obj
