from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(email, username, password, **extra_fields):
        """
        World-class user registration service ensuring atomic integrity.
        """
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields
        )
        return user
