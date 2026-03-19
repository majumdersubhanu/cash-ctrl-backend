from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Account


@admin.register(Account)
class AccountAdmin(ImportExportModelAdmin):
    list_display = ("id", "user", "name", "balance", "currency", "created_at")
    list_filter = ("currency", "created_at")
    search_fields = ("name", "user__email")
    readonly_fields = ("created_at",)
