import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class TruecallerService:
    @staticmethod
    def verify_profile(request_payload):
        """
        Verifies the Truecaller user profile using the verify profile API.
        Ref: https://docs.truecaller.com/truecaller-sdk/web/verify-user-with-truecaller-server-side
        """
        partner_key = getattr(settings, "TRUECALLER_PARTNER_KEY", None)
        if not partner_key:
            logger.error("TRUECALLER_PARTNER_KEY not configured.")
            return None

        # This is a stub for the verification logic
        # Usually involves checking the request signature and calling Truecaller API
        logger.info(
            f"Attempting Truecaller verification for payload: {request_payload}. Partner Key available: {bool(partner_key)}"
        )

        # Mocking successful verification for now
        return {
            "status": "success",
            "phone": request_payload.get("phone_number"),
            "name": request_payload.get("name"),
        }


class CashfreeService:
    @staticmethod
    def verify_aadhaar(aadhaar_number):
        """
        Verifies Aadhaar using Cashfree Verification API.
        """
        app_id = getattr(settings, "CASHFREE_APP_ID", None)
        secret = getattr(settings, "CASHFREE_SECRET_KEY", None)

        logger.info(
            f"Calling Cashfree Aadhaar verification for: {aadhaar_number[:4]}xxxx. Configured: {bool(app_id and secret)}"
        )

        # Mocking API response
        return {"status": "SUCCESS", "message": "Aadhaar verified successfully"}


class SetuService:
    @staticmethod
    def create_account_linking_request(user_id):
        """
        Creates an account linking request via Setu Account Aggregator.
        """
        client_id = getattr(settings, "SETU_CLIENT_ID", None)

        logger.info(
            f"Creating Setu account linking request for user: {user_id}. Client ID available: {bool(client_id)}"
        )

        # Mocking Setu session link
        return {
            "session_url": "https://setu.co/aa/mock-session-123",
            "request_id": "req_5678",
        }
