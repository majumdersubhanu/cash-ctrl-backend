from django.contrib import admin

from .models import Loan, Installment


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lender",
        "borrower",
        "amount",
        "interest_rate",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("borrower__email", "lender__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ("id", "loan", "amount", "due_date", "status")
    list_filter = ("status", "due_date")
    search_fields = ("loan__id", "loan__borrower__email")
