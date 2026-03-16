from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import KYCProfile
from .serializers import KYCProfileSerializer, KYCDocumentSerializer
from .services import KYCService

class KYCViewSet(viewsets.ModelViewSet):
    serializer_class = KYCProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return KYCProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return KYCService.get_or_create_profile(self.request.user)

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def submit(self, request):
        profile = self.get_object()
        if KYCService.submit_for_verification(profile):
            return Response({"status": "PENDING", "message": "Verification submitted."})
        return Response(
            {"error": "Incomplete profile. Ensure name and documents are provided."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'], url_path='upload-document')
    def upload_document(self, request):
        profile = self.get_object()
        serializer = KYCDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
