from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from rangefilter.filters import DateRangeFilter, NumericRangeFilter

from .models import Transaction, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "type", "created_at")
    list_filter = ("type", "created_at")
    search_fields = ("name", "user__email")


@admin.register(Transaction)
class TransactionAdmin(ImportExportModelAdmin):
    list_display = ("id", "user", "account", "type", "amount", "status", "date")
    list_filter = (
        "type",
        "status",
        ("date", DateRangeFilter),
        ("amount", NumericRangeFilter),
    )
    search_fields = ("description", "user__email", "account__name")
    date_hierarchy = "date"

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("user", "account", "category")
        )
