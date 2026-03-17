from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class KYCProfile(models.Model):
    class KYCStatus(models.TextChoices):
        UNVERIFIED = "UNVERIFIED", _("Unverified")
        PENDING = "PENDING", _("Pending")
        VERIFIED = "VERIFIED", _("Verified")
        REJECTED = "REJECTED", _("Rejected")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="kyc_profile"
    )
    status = models.CharField(
        max_length=20, choices=KYCStatus.choices, default=KYCStatus.UNVERIFIED
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"KYC for {self.user.email} - {self.status}"


class KYCDocument(models.Model):
    class DocumentType(models.TextChoices):
        PASSPORT = "PASSPORT", _("Passport")
        ID_CARD = "ID_CARD", _("ID Card")
        DRIVERS_LICENSE = "DRIVERS_LICENSE", _("Drivers License")
        UTILITY_BILL = "UTILITY_BILL", _("Utility Bill")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        KYCProfile, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    document_file = models.FileField(upload_to="kyc_documents/%Y/%m/%d/")

    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} for {self.profile.user.email}"
