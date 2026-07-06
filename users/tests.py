import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from model_bakery import baker

from users.services import UserService
from users.backends import DualAuthBackend
from users.phone_auth_service import PhoneAuthService

User = get_user_model()


# ---------------------------------------------------------------------------
# UserService Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserService:
    def test_create_user_success(self):
        """Test user creation with valid email and password."""
        email = "testuser@cashctrl.com"
        password = "securepassword123"
        user = UserService.create_user(email=email, password=password)

        assert user.email == email
        assert user.username.startswith("testuser_")
        assert user.check_password(password) is True
        assert User.objects.count() == 1

    def test_create_user_with_explicit_username(self):
        """Test user creation when a username is explicitly provided."""
        email = "custom_un@cashctrl.com"
        password = "securepassword123"
        username = "custom_username_xyz"

        user = UserService.create_user(
            email=email, password=password, username=username
        )

        assert user.email == email
        assert user.username == username

    def test_create_user_missing_email(self):
        """Ensure ValueError is raised if email and phone are missing."""
        with pytest.raises(ValueError, match="Email or Phone Number must be set"):
            UserService.create_user(email="", password="securepassword123")

    def test_create_user_auto_generates_username_from_email(self):
        """Username is derived from email prefix + random hex when not given."""
        user = UserService.create_user(email="alice@example.com", password="pass123")
        assert user.username.startswith("alice_")
        assert len(user.username) > len("alice_")  # has random suffix

    def test_create_user_no_password_sets_unusable(self):
        """If no password is given, user gets an unusable password."""
        user = UserService.create_user(email="nopass@example.com")
        assert not user.has_usable_password()


# ---------------------------------------------------------------------------
# DualAuthBackend Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDualAuthBackend:
    def setup_method(self):
        self.backend = DualAuthBackend()
        self.password = "securepass123"
        self.user = UserService.create_user(
            email="dual@example.com",
            phone_number="+12025550100",
            password=self.password,
        )

    def test_authenticate_with_email(self):
        """Should authenticate using email as username."""
        result = self.backend.authenticate(
            request=None, username="dual@example.com", password=self.password
        )
        assert result == self.user

    def test_authenticate_with_phone_number(self):
        """Should authenticate using phone number as username."""
        result = self.backend.authenticate(
            request=None, username="+12025550100", password=self.password
        )
        assert result == self.user

    def test_authenticate_wrong_password(self):
        """Should return None for wrong password."""
        result = self.backend.authenticate(
            request=None, username="dual@example.com", password="wrongpassword"
        )
        assert result is None

    def test_authenticate_nonexistent_user(self):
        """Should return None for user that doesn't exist."""
        result = self.backend.authenticate(
            request=None, username="nobody@example.com", password="somepassword"
        )
        assert result is None

    def test_authenticate_username_from_kwargs(self):
        """Should pick up username from kwargs when not passed positionally."""
        result = self.backend.authenticate(
            request=None, password=self.password, email="dual@example.com"
        )
        # username is None; falls back to kwargs.get(User.USERNAME_FIELD) = email
        assert result == self.user

    def test_authenticate_inactive_user_returns_none(self):
        """Inactive users cannot authenticate."""
        self.user.is_active = False
        self.user.save()
        result = self.backend.authenticate(
            request=None, username="dual@example.com", password=self.password
        )
        assert result is None


# ---------------------------------------------------------------------------
# PhoneAuthService Tests
# ---------------------------------------------------------------------------


class TestPhoneAuthService:
    """
    These tests do NOT need the DB; they only interact with Django's cache.
    """

    def setup_method(self):
        cache.clear()

    def teardown_method(self):
        cache.clear()

    def test_send_otp_returns_six_digit_string(self):
        """send_otp should return a 6-digit numeric string."""
        otp = PhoneAuthService.send_otp("+12025550199")
        assert otp.isdigit()
        assert len(otp) == 6

    def test_send_otp_stores_in_cache(self):
        """After send_otp, the OTP should be retrievable from the cache."""
        phone = "+12025550200"
        otp = PhoneAuthService.send_otp(phone)
        cached = cache.get(f"otp_{phone}")
        assert cached == otp

    def test_verify_otp_success(self):
        """verify_otp returns True for correct OTP."""
        phone = "+12025550201"
        otp = PhoneAuthService.send_otp(phone)
        result = PhoneAuthService.verify_otp(phone, otp)
        assert result is True

    def test_verify_otp_deletes_cache_entry(self):
        """After successful verification, the OTP must be deleted from cache."""
        phone = "+12025550202"
        otp = PhoneAuthService.send_otp(phone)
        PhoneAuthService.verify_otp(phone, otp)
        assert cache.get(f"otp_{phone}") is None

    def test_verify_otp_wrong_otp_raises(self):
        """Wrong OTP raises ValidationError with 'Invalid OTP'."""
        from rest_framework.exceptions import ValidationError

        phone = "+12025550203"
        PhoneAuthService.send_otp(phone)
        with pytest.raises(ValidationError, match="Invalid OTP"):
            PhoneAuthService.verify_otp(phone, "000000")

    def test_verify_otp_expired_raises(self):
        """If no OTP in cache, raises ValidationError with 'OTP expired'."""
        from rest_framework.exceptions import ValidationError

        phone = "+12025550204"
        with pytest.raises(ValidationError, match="OTP expired or not found"):
            PhoneAuthService.verify_otp(phone, "123456")

    def test_send_otp_overwrites_existing(self):
        """Calling send_otp twice replaces the previous OTP in cache."""
        phone = "+12025550205"
        PhoneAuthService.send_otp(phone)
        otp2 = PhoneAuthService.send_otp(phone)
        cached = cache.get(f"otp_{phone}")
        assert cached == otp2
        # otp1 may equal otp2 by chance; but the stored value is the latest
        assert cached is not None


@pytest.mark.django_db
class TestUserManagerAndModel:
    def test_create_user_raises_value_error_if_no_email_and_phone(self):
        with pytest.raises(ValueError, match="Email or Phone Number must be set"):
            User.objects.create_user()

    def test_create_user_without_password_sets_unusable(self):
        user = User.objects.create_user(phone_number="+18005550199")
        assert not user.has_usable_password()

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com", password="adminpassword"
        )
        assert superuser.is_staff
        assert superuser.is_superuser
        assert superuser.email == "admin@example.com"

    def test_user_str_representation(self):
        user_email = User(email="test@example.com")
        assert str(user_email) == "test@example.com"

        user_phone = User(phone_number="+18005550199")
        assert str(user_phone) == "+18005550199"

        user_username = User(username="my_username")
        assert str(user_username) == "my_username"


@pytest.mark.django_db
class TestUserSerializers:
    def test_user_registration_serializer_password_mismatch(self):
        from users.serializers import UserRegistrationSerializer
        from rest_framework.exceptions import ValidationError

        data = {
            "email": "mismatch@example.com",
            "password": "password123",
            "password_confirm": "password456",
        }
        serializer = UserRegistrationSerializer(data=data)
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Password fields didn't match" in str(excinfo.value)

    def test_custom_token_serializer_no_user(self):
        from users.serializers import CustomTokenSerializer

        data = {
            "access": "fake_access_token",
            "refresh": "fake_refresh_token",
            "user": None,
        }
        serializer = CustomTokenSerializer(data)
        assert serializer.data["kyc_status"] == "UNVERIFIED"
        assert serializer.data["redirect_to"] == "/onboarding/kyc"

    def test_custom_token_serializer_verified_user(self):
        from users.serializers import CustomTokenSerializer

        user = baker.make(User, email="verified@example.com")
        profile = getattr(user, "kyc_profile", None)
        if not profile:
            from onboarding.models import KYCProfile

            profile = KYCProfile.objects.create(user=user)
        profile.status = "VERIFIED"
        profile.save()

        data = {
            "access": "fake_access_token",
            "refresh": "fake_refresh_token",
            "user": user,
        }
        serializer = CustomTokenSerializer(data)
        assert serializer.data["kyc_status"] == "VERIFIED"
        assert serializer.data["redirect_to"] == "/dashboard"
