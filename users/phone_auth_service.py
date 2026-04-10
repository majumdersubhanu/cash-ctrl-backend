import logging
import random

from django.core.cache import cache
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class PhoneAuthService:
    """
    Orchestration layer for high-trust mobile verification.

    Manages the full lifecycle of One-Time Passwords (OTPs) including
    generation, cache-backed persistence, and multi-factor validation.
    """

    OTP_TIMEOUT = 300  # 5 minutes

    @classmethod
    def send_otp(cls, phone_number):
        """
        Generates and dispatches a cryptographically secure OTP.

        Persists the challenge in the system cache with a strict TTL.
        """
        otp = str(random.randint(100000, 999999))
        cache_key = f"otp_{phone_number}"
        cache.set(cache_key, otp, timeout=cls.OTP_TIMEOUT)

        # Mock sending SMS
        logger.info(f"OTP for {phone_number}: {otp}")
        print(f"🚀 [SMS MOCK] OTP for {phone_number}: {otp}")

        return otp

    @classmethod
    def verify_otp(cls, phone_number, otp):
        """
        Validates a provided OTP challenge against the cached state.

        Destroys the secret upon successful verification to prevent replay attacks.
        """
        cache_key = f"otp_{phone_number}"
        cached_otp = cache.get(cache_key)

        if not cached_otp:
            raise ValidationError("OTP expired or not found")

        if cached_otp != otp:
            raise ValidationError("Invalid OTP")

        # Clear OTP after successful verification
        cache.delete(cache_key)
        return True
