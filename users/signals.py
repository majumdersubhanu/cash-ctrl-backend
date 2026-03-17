from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from onboarding.models import KYCProfile
from accounts.models import WalletAccount

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_dependencies(sender, instance, created, **kwargs):
    """
    Hook to automatically orchestrate related platform provisioning:
    1. Pending KYC Profile for compliance state tracking.
    2. Primary WalletAccount for immediate transaction readiness.
    Ensures seamless Developer Experience and automates multi-step pipelines.
    """
    if created:
        KYCProfile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            status="PENDING",
        )
        
        WalletAccount.objects.create(
            user=instance,
            name="Main Wallet",
            wallet_provider="System CashCtrl Gateway"
        )
