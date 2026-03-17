import pytest
from django.contrib.auth import get_user_model
from users.services import UserService

User = get_user_model()

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
        
        user = UserService.create_user(email=email, password=password, username=username)
        
        assert user.email == email
        assert user.username == username

    def test_create_user_missing_email(self):
        """Ensure ValueError is raised if email is missing."""
        with pytest.raises(ValueError, match="The Email field must be set"):
            UserService.create_user(email="", password="securepassword123")
