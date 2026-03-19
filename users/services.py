from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class UserService:
    """
    World-class user registration service ensuring atomic integrity.

    Orchestrates the lifecycle of user creation across multiple identity providers
    (Email, Phone, Google).
    """

    @staticmethod
    @transaction.atomic
    def create_user(
            email=None, phone_number=None, password=None, username=None, **extra_fields
    ):
        """
        Creates a new user record atomically.

        Handles diverse registration entry points and auto-generates secure,
        collision-resistant usernames when necessary.
        """
        if not username:
            import secrets

            ident = email.split("@")[0] if email else str(phone_number)
            username = f"{ident}_{secrets.token_hex(4)}"

        user = User.objects.create_user(
            email=email,
            phone_number=phone_number,
            username=username,
            password=password,
            **extra_fields,
        )
        return user
