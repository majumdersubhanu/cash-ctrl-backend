from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'resource_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'resource_type', 'timestamp')
    search_fields = ('user__email', 'action', 'resource_id', 'ip_address')
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
