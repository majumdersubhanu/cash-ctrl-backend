from django.contrib import admin

from .models import RecurringTransaction


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "user",
        "amount",
        "interval",
        "next_execution",
        "is_active",
    )
    list_filter = ("interval", "is_active", "next_execution")
    search_fields = ("description", "user__email")
