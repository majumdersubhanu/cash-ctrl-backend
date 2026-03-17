from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from transactions.models import Transaction


class ForecastingService:
    """
    Predictive engine utilizing historical transaction patterns to project future states.

    Leverages time-series aggregation to provide actionable financial insights.
    """

    @staticmethod
    def predict_next_month_spending(user):
        """
        Calculates a statistical projection for the user's spending in the next cycle.

        Methodology: 3-month rolling average of verified outgoing 'POSTED' expenses.
        """
        now = timezone.now()
        three_months_ago = now - timedelta(days=90)

        # Get historical monthly spends
        history = (
            Transaction.objects.filter(
                user=user, type="EXPENSE", status="POSTED", date__gte=three_months_ago
            )
            .values("date__month")
            .annotate(total=Sum("amount"))
        )

        if not history:
            return Decimal("0.00")

        total_spent = sum(item["total"] for item in history)
        months_count = len(history)

        return (total_spent / Decimal(str(months_count))).quantize(Decimal("0.01"))

    @staticmethod
    def forecast_cash_flow(user, days=30):
        """
        Estimates the net liquidity shift over a projected horizon.

        Methodology: Projects current net daily velocity (Inflow - Outflow) over
        the specified window.
        """
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        incoming = (
            Transaction.objects.filter(
                user=user, type="INCOME", status="POSTED", date__gte=thirty_days_ago
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        outgoing = (
            Transaction.objects.filter(
                user=user, type="EXPENSE", status="POSTED", date__gte=thirty_days_ago
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        net_daily = (Decimal(str(incoming)) - Decimal(str(outgoing))) / Decimal("30")

        return (net_daily * Decimal(str(days))).quantize(Decimal("0.01"))
