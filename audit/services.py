from .models import AuditLog


class AuditService:
    @staticmethod
    def log_action(
        user, action, resource_type, resource_id=None, changes=None, ip_address=None
    ):
        """
        Records a detailed immutable event in the system audit trail.
        Captures the actor, the specific business action, the targeted cloud resource, 
        and any state changes for compliance and security forensics.
        """
        return AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            changes=changes,
            ip_address=ip_address,
        )
