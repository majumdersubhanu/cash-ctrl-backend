from .models import AuditLog


class AuditService:
    @staticmethod
    def log_action(
        user, action, resource_type, resource_id=None, changes=None, ip_address=None
    ):
        """
        Creates an audit log entry.
        """
        return AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            changes=changes,
            ip_address=ip_address,
        )
