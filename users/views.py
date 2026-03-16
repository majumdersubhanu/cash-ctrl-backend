from rest_framework import generics, permissions
from .serializers import UserRegistrationSerializer, UserSerializer

class RegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        """
        Extending create flow if needed, but the logic is already in the serializer/service.
        """
        super().perform_create(serializer)

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
