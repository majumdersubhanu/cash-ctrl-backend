from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "password_confirm")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def save(self, request=None, **kwargs):
        """
        Custom save method tailored for dj-rest-auth integration, which
        injects the HTTP request as a kwarg natively during signups.
        """
        validated_data = dict(list(self.validated_data.items()) + list(kwargs.items()))
        validated_data.pop("password_confirm", None)

        from .services import UserService

        user = UserService.create_user(**validated_data)
        self.instance = user
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "first_name", "last_name", "profile_picture")
        read_only_fields = ("id", "email", "phone_number")


class PhoneAuthSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class PhoneVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField(max_length=6)


class CustomTokenSerializer(serializers.Serializer):
    """
    Overrides the default dj-rest-auth token payload to inject the
    user's KYC state and a frontend navigational redirect flag.
    """

    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    kyc_status = serializers.SerializerMethodField()
    redirect_to = serializers.SerializerMethodField()

    def get_kyc_status(self, obj):
        user = obj.get("user")
        if not user:
            return "UNVERIFIED"
        profile = getattr(user, "kyc_profile", None)
        return profile.status if profile else "UNVERIFIED"

    def get_redirect_to(self, obj):
        status = self.get_kyc_status(obj)
        if status != "VERIFIED":
            return "/onboarding/kyc"
        return "/dashboard"
