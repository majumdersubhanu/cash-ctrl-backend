from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send_notification(user, title, message, type="INFO"):
        """
        Creates a system notification for the user.
        """
        return Notification.objects.create(
            user=user, title=title, message=message, type=type
        )

    @staticmethod
    def alert_budget_limit(user, budget, current_spend):
        """
        Alerts user when they approach or exceed budget.
        """
        if current_spend >= budget.amount:
            NotificationService.send_notification(
                user=user,
                title=f"Budget Exceeded: {budget.category.name}",
                message=f"You have spent {current_spend} which exceeds your budget of {budget.amount}.",
                type="ALERT",
            )
        elif current_spend >= (budget.amount * 0.9):
            NotificationService.send_notification(
                user=user,
                title=f"Budget Warning: {budget.category.name}",
                message=f"You have spent {current_spend}, reaching 90% of your {budget.amount} budget.",
                type="WARNING",
            )
