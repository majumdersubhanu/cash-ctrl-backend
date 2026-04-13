from django.contrib import admin

from .models import KYCProfile, KYCDocument


class KYCDocumentInline(admin.TabularInline):
    model = KYCDocument
    extra = 0


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "first_name", "last_name", "verified_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "first_name", "last_name")
    inlines = [KYCDocumentInline]


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ("profile", "document_type", "is_verified", "uploaded_at")
    list_filter = ("document_type", "is_verified")
