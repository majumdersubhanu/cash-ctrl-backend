from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    PhoneAuthSerializer,
    PhoneVerifySerializer,
    CustomTokenSerializer,
)
from .phone_auth_service import PhoneAuthService
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


@extend_schema_view(
    post=extend_schema(
        summary="Register User",
        description="Public endpoint to register a new user using their Email and Password.",
        tags=["Authentication"],
        operation_id="register"
    )
)
class RegistrationView(generics.CreateAPIView):
    """
    Public registration gateway for new users.
    Returns JWT tokens and user profile upon success.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user,
        }
        return Response(CustomTokenSerializer(data).data, status=status.HTTP_201_CREATED)


class PhoneAuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet to handle phone-based OTP authentication.
    """

    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        request=PhoneAuthSerializer,
        responses={200: {"example": {"message": "OTP sent successfully"}}},
        tags=["Authentication"],
        summary="Request OTP",
        operation_id="request_otp"
    )
    @action(detail=False, methods=["post"])
    def request_otp(self, request):
        serializer = PhoneAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        PhoneAuthService.send_otp(phone_number)
        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)

    @extend_schema(
        request=PhoneVerifySerializer,
        responses={200: CustomTokenSerializer},
        tags=["Authentication"],
        summary="Verify OTP",
        operation_id="verify_otp"
    )
    @action(detail=False, methods=["post"])
    def verify_otp(self, request):
        serializer = PhoneVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        otp = serializer.validated_data["otp"]

        # Verify OTP
        PhoneAuthService.verify_otp(phone_number, otp)

        # Get or create user
        from .models import User

        user, created = User.objects.get_or_create(
            phone_number=phone_number, defaults={"username": f"user_{phone_number}"}
        )

        if created:
            user.set_unusable_password()
            user.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Use CustomTokenSerializer format
        data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": user,
        }
        return Response(CustomTokenSerializer(data).data, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(summary="Get Current User Profile", tags=["Profiles"], operation_id="get_profile"),
    put=extend_schema(summary="Update Current User Profile", tags=["Profiles"], operation_id="update_profile"),
    patch=extend_schema(
        summary="Partially Update Current User Profile", tags=["Profiles"], operation_id="partial_update_profile"
    ),
)
class MeView(generics.RetrieveUpdateAPIView):
    """
    Core profile gateway. Allows a user to view and safely mutate their own root state.
    """

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema_view(
    post=extend_schema(
        summary="Google Login",
        tags=["Authentication"],
        operation_id="google_login"
    )
)
class GoogleLogin(SocialLoginView):
    """
    Google social login bridge.
    """

    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/callback/google"
    client_class = OAuth2Client
