from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer

class RegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        """
        Extending create flow if needed, but the logic is already in the serializer/service.
        """
        super().perform_create(serializer)
