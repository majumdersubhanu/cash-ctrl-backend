from django.db import models
import uuid

class ExchangeRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_currency = models.CharField(max_length=3, default='USD')
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=6)
    
    provider = models.CharField(max_length=50, default='manual')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('base_currency', 'target_currency')

    def __str__(self):
        return f"1 {self.base_currency} = {self.rate} {self.target_currency}"

    @classmethod
    def get_rate(cls, from_curr, to_curr):
        if from_curr == to_curr:
            return 1.0
        
        # Try direct rate
        try:
            return cls.objects.get(base_currency=from_curr, target_currency=to_curr).rate
        except cls.DoesNotExist:
            # Try inverse rate
            try:
                inverse = cls.objects.get(base_currency=to_curr, target_currency=from_curr).rate
                return 1 / inverse
            except cls.DoesNotExist:
                # Fallback to USD as intermediary if needed, but for now error out or return 1
                return None
