from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(email, password, username=None, **extra_fields):
        """
        World-class user registration service ensuring atomic integrity.
        Auto-generates a username if none is supplied via Dj-Rest-Auth email registration.
        """
        if not username:
            import secrets
            username = email.split("@")[0] + "_" + secrets.token_hex(4)
        
        user = User.objects.create_user(
            email=email, username=username, password=password, **extra_fields
        )
        return user
