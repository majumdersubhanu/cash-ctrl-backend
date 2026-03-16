from django.utils import timezone
from .models import KYCProfile

class KYCService:
    @staticmethod
    def get_or_create_profile(user):
        profile, created = KYCProfile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    def submit_for_verification(profile):
        """
        Transitions profile to PENDING status if basic info exists.
        """
        if profile.first_name and profile.last_name and profile.documents.exists():
            profile.status = 'PENDING'
            profile.save()
            return True
        return False

    @staticmethod
    def verify_profile(profile):
        """
        Marks profile as VERIFIED (usually by an admin).
        """
        profile.status = 'VERIFIED'
        profile.verified_at = timezone.now()
        profile.save()
        return True

    @staticmethod
    def reject_profile(profile, reason=None):
        """
        Rejects a profile.
        """
        profile.status = 'REJECTED'
        profile.save()
        # In a real app, we'd send a notification/email with the reason
        return True
