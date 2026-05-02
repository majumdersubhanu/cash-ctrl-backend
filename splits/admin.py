from django.contrib import admin

from .models import SplitGroup, SplitExpense, SplitParticipation


class SplitParticipationInline(admin.TabularInline):
    model = SplitParticipation
    extra = 0


@admin.register(SplitGroup)
class SplitGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "creator", "created_at")
    search_fields = ("name", "creator__email")
    filter_horizontal = ("members",)


@admin.register(SplitExpense)
class SplitExpenseAdmin(admin.ModelAdmin):
    list_display = ("description", "group", "paid_by", "amount", "currency", "date")
    list_filter = ("currency", "date")
    inlines = [SplitParticipationInline]
