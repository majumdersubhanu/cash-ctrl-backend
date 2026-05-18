from django.contrib import admin

from .models import Budget, SavingsGoal


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("category", "user", "amount", "period", "start_date")
    list_filter = ("period", "start_date")
    search_fields = ("user__email", "category__name")


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "target_amount", "current_amount", "is_completed")
    list_filter = ("is_completed", "target_date")
    search_fields = ("name", "user__email")
