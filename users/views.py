from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import UserRegistrationSerializer, UserSerializer


@extend_schema_view(
    post=extend_schema(summary="Register User", description="Public endpoint to register a new user using their Email and Password. A custom auth flow will trigger automatically.", tags=["Authentication"])
)
class RegistrationView(generics.CreateAPIView):
    """
    Public registration gateway for new users.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        """
        Extending create flow if needed, but the logic is already in the serializer/service.
        """
        super().perform_create(serializer)


@extend_schema_view(
    get=extend_schema(summary="Get Current User Profile", description="Returns detailed profile data (including nested settings) for the currently authenticated user.", tags=["Authentication"]),
    put=extend_schema(summary="Update Current User Profile", tags=["Authentication"]),
    patch=extend_schema(summary="Partially Update Current User Profile", tags=["Authentication"]),
)
class MeView(generics.RetrieveUpdateAPIView):
    """
    Core profile gateway. Allows a user to view and safely mutate their own root state.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
