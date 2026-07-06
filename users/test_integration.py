import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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


@pytest.mark.django_db
class TestPhoneAuthAPI:
    def test_request_otp(self, api_client):
        url = "/api/v1/users/phone/request_otp/"
        payload = {"phone_number": "+1234567890"}
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "OTP sent successfully"

    def test_verify_otp_success_new_user(self, api_client):
        # 1. request OTP to populate cache
        phone = "+1999888777"
        api_client.post(
            "/api/v1/users/phone/request_otp/", {"phone_number": phone}, format="json"
        )
        # get OTP from cache
        from django.core.cache import cache

        otp = cache.get(f"otp_{phone}")

        # 2. verify OTP
        url = "/api/v1/users/phone/verify_otp/"
        payload = {"phone_number": phone, "otp": otp}
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert User.objects.filter(phone_number=phone).exists()

    def test_verify_otp_existing_user(self, api_client):
        phone = "+1777666555"
        User.objects.create(phone_number=phone, username="existing_phone_user")

        api_client.post(
            "/api/v1/users/phone/request_otp/", {"phone_number": phone}, format="json"
        )
        from django.core.cache import cache

        otp = cache.get(f"otp_{phone}")

        url = "/api/v1/users/phone/verify_otp/"
        payload = {"phone_number": phone, "otp": otp}
        response = api_client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert User.objects.filter(phone_number=phone).count() == 1


@pytest.mark.django_db
class TestMeAPI:
    def test_get_me(self, api_client):
        user = User.objects.create(email="me@example.com", username="me_user")
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "me@example.com"

    def test_put_me(self, api_client):
        user = User.objects.create(
            email="me2@example.com", username="me2_user", first_name="A", last_name="B"
        )
        api_client.force_authenticate(user=user)
        data = {
            "email": "me2@example.com",
            "username": "me2_user",
            "first_name": "Updated",
            "last_name": "B",
        }
        response = api_client.put("/api/v1/users/me/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"
