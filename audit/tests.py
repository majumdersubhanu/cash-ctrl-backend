import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from audit.services import AuditService

User = get_user_model()


@pytest.mark.django_db
class TestAuditLog:
    def test_audit_log_str(self):
        user = baker.make(User, email="auditor@example.com")
        log = AuditService.log_action(
            user=user, action="USER_LOGIN", resource_type="User", resource_id=user.id
        )
        assert str(log) == f"auditor@example.com - USER_LOGIN - {log.timestamp}"

    def test_audit_log_str_no_user(self):
        log = AuditService.log_action(
            user=None, action="SYSTEM_BOOT", resource_type="System"
        )
        assert str(log) == f"None - SYSTEM_BOOT - {log.timestamp}"
