from decimal import Decimal

import pytest
from model_bakery import baker

from notifications.models import Notification
from notifications.services import NotificationService


@pytest.mark.django_db
class TestNotificationService:
    """Tests for NotificationService.send_notification"""

    def test_send_notification_creates_db_record(self):
        """send_notification should persist a Notification object."""
        user = baker.make("users.User")
        notif = NotificationService.send_notification(
            user=user, title="Hello", message="World"
        )
        assert notif.pk is not None
        assert Notification.objects.filter(pk=notif.pk).exists()
        assert str(notif) == f"Hello for {user.email}"

    def test_send_notification_defaults_to_info_type(self):
        """Default notification type is 'INFO'."""
        user = baker.make("users.User")
        notif = NotificationService.send_notification(
            user=user, title="Info Note", message="Some info"
        )
        assert notif.type == "INFO"

    def test_send_notification_custom_type(self):
        """Passing a type overrides the default."""
        user = baker.make("users.User")
        notif = NotificationService.send_notification(
            user=user, title="Alert!", message="Danger!", type="ALERT"
        )
        assert notif.type == "ALERT"

    def test_send_notification_warning_type(self):
        user = baker.make("users.User")
        notif = NotificationService.send_notification(
            user=user, title="Warn", message="Close to limit", type="WARNING"
        )
        assert notif.type == "WARNING"

    def test_send_notification_success_type(self):
        user = baker.make("users.User")
        notif = NotificationService.send_notification(
            user=user, title="Done", message="Paid!", type="SUCCESS"
        )
        assert notif.type == "SUCCESS"

    def test_send_notification_links_to_user(self):
        user = baker.make("users.User")
        notif = NotificationService.send_notification(user=user, title="T", message="M")
        assert notif.user == user

    def test_send_notification_default_read_is_false(self):
        user = baker.make("users.User")
        notif = NotificationService.send_notification(user=user, title="T", message="M")
        assert notif.read is False


@pytest.mark.django_db
class TestAlertBudgetLimit:
    """Tests for NotificationService.alert_budget_limit"""

    def _make_budget(self, amount):
        """Helper to build a budget mock with the right shape."""
        category = baker.make("transactions.Category", name="Groceries")
        budget = baker.make(
            "analytics.Budget",
            amount=Decimal(str(amount)),
            category=category,
        )
        return budget

    def test_budget_exceeded_creates_alert_notification(self):
        """When current_spend >= budget.amount, an ALERT notification is created."""
        user = baker.make("users.User")
        budget = self._make_budget(100)

        NotificationService.alert_budget_limit(
            user, budget, current_spend=Decimal("100")
        )

        notif = Notification.objects.get(user=user)
        assert notif.type == "ALERT"
        assert "Budget Exceeded" in notif.title
        assert "Groceries" in notif.title

    def test_budget_exceeded_over_limit(self):
        """Spending more than budget also triggers ALERT."""
        user = baker.make("users.User")
        budget = self._make_budget(100)

        NotificationService.alert_budget_limit(
            user, budget, current_spend=Decimal("150")
        )

        notif = Notification.objects.get(user=user)
        assert notif.type == "ALERT"

    def test_budget_warning_at_90_percent(self):
        """At exactly 90% of budget, a WARNING notification is created."""
        user = baker.make("users.User")
        budget = self._make_budget(100)

        NotificationService.alert_budget_limit(
            user, budget, current_spend=Decimal("90")
        )

        notif = Notification.objects.get(user=user)
        assert notif.type == "WARNING"
        assert "Budget Warning" in notif.title

    def test_budget_warning_between_90_and_100(self):
        """At 95% of budget, a WARNING is sent."""
        user = baker.make("users.User")
        budget = self._make_budget(100)

        NotificationService.alert_budget_limit(
            user, budget, current_spend=Decimal("95")
        )

        notif = Notification.objects.get(user=user)
        assert notif.type == "WARNING"

    def test_no_notification_below_90_percent(self):
        """Below 90%, no notification should be created."""
        user = baker.make("users.User")
        budget = self._make_budget(100)

        NotificationService.alert_budget_limit(
            user, budget, current_spend=Decimal("89")
        )

        assert Notification.objects.filter(user=user).count() == 0

    def test_no_notification_at_zero_spend(self):
        """Zero spend produces no notification."""
        user = baker.make("users.User")
        budget = self._make_budget(100)

        NotificationService.alert_budget_limit(user, budget, current_spend=Decimal("0"))

        assert Notification.objects.filter(user=user).count() == 0

    def test_alert_message_contains_amounts(self):
        """ALERT message body contains the spend and budget amounts."""
        user = baker.make("users.User")
        budget = self._make_budget(200)

        NotificationService.alert_budget_limit(
            user, budget, current_spend=Decimal("200")
        )

        notif = Notification.objects.get(user=user)
        assert "200" in notif.message
