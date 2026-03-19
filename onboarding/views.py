from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from audit.services import AuditService
from .models import KYCProfile
from .serializers import KYCProfileSerializer, KYCDocumentSerializer
from .services import KYCService


@extend_schema_view(
    list=extend_schema(
        summary="Get KYC Profile Status",
        description="Retrieve the current verification state of the user's KYC profile. Returns essential metadata including verification level and pending document requirements.",
        tags=["KYC & Onboarding"],
    ),
    retrieve=extend_schema(
        summary="Inspect specific KYC details",
        description="Detailed view of the user's identity profile, including PII and submitted verification tokens.",
        tags=["KYC & Onboarding"],
    ),
    submit=extend_schema(
        summary="Submit for identity verification",
        description="Initiates the manual or automated background check. This action is immutable once the profile enters 'PENDING' state.",
        tags=["KYC & Onboarding"],
    ),
    upload_document=extend_schema(
        summary="Upload identity documents",
        description="Securely ingest proof-of-identity or proof-of-address documents. Supports multiple document types (Passport, Utility Bill, etc.) with encrypted storage handles.",
        tags=["KYC & Onboarding"],
    ),
)
class KYCViewSet(viewsets.ModelViewSet):
    """
    Gateway to the user identity verification lifecycle.
    """

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

    @action(detail=False, methods=["post"], throttle_classes=[UserRateThrottle])
    def submit(self, request):
        profile = self.get_object()
        if KYCService.submit_for_verification(profile):
            AuditService.log_action(
                user=request.user,
                action="KYC_SUBMITTED",
                resource_type="KYCProfile",
                resource_id=profile.id,
                ip_address=request.META.get("REMOTE_ADDR"),
            )
            return Response({"status": "PENDING", "message": "Verification submitted."})
        return Response(
            {"error": "Incomplete profile. Ensure name and documents are provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"], url_path="upload-document")
    def upload_document(self, request):
        profile = self.get_object()
        serializer = KYCDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
