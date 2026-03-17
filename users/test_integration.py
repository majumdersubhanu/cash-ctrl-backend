import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestUserRegistrationAPI:
    def test_user_registration_api_success(self, api_client):
        """Test integration of the DJ-Rest-Auth custom registration endpoint."""
        url = reverse("register")
        payload = {
            "email": "api_test@cashctrl.com",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }

        response = api_client.post(url, payload, format="json")
        print(f"DEBUG Response Data: {response.data}")

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["kyc_status"] == "PENDING"
        assert response.data["redirect_to"] == "/onboarding/kyc"

        # Verify database insertion
        assert User.objects.filter(email=payload["email"]).exists()
