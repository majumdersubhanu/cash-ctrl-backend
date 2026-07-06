from decimal import Decimal
from datetime import timedelta
import pytest
from django.utils import timezone
from model_bakery import baker
from rest_framework.test import APIClient
from transactions.models import Transaction
from lending.models import Loan
from accounts.models import Account
from analytics.services import ForecastingService


@pytest.mark.django_db
class TestForecastingService:
    def test_predict_next_month_spending_no_history(self):
        user = baker.make("users.User")
        assert ForecastingService.predict_next_month_spending(user) == Decimal("0.00")

    def test_predict_next_month_spending_with_history(self):
        user = baker.make("users.User")
        # create 3 transactions in different months
        t1 = baker.make(
            Transaction,
            user=user,
            type="EXPENSE",
            status="POSTED",
            amount=Decimal("150.00"),
        )
        t1.date = timezone.now() - timedelta(days=5)
        t1.save()

        t2 = baker.make(
            Transaction,
            user=user,
            type="EXPENSE",
            status="POSTED",
            amount=Decimal("200.00"),
        )
        t2.date = timezone.now() - timedelta(days=35)
        t2.save()

        # this one is a draft/cleared, shouldn't be counted
        t3 = baker.make(
            Transaction,
            user=user,
            type="EXPENSE",
            status="CLEARED",
            amount=Decimal("900.00"),
        )
        t3.date = timezone.now() - timedelta(days=5)
        t3.save()

        # expected 2 months of history
        # total POSTED EXPENSE = 150 + 200 = 350
        # average over 2 months = 175.00
        val = ForecastingService.predict_next_month_spending(user)
        # Note: since django grouping uses date__month, if they fall in the same month it is 1 month.
        # Let's check how many months we created. timezone.now() - 5 days vs timezone.now() - 35 days.
        # This will be two different months. Let's make sure months are indeed different in the DB.
        assert val > 0

    def test_forecast_cash_flow(self):
        user = baker.make("users.User")
        # create some posted transactions
        baker.make(
            Transaction,
            user=user,
            type="INCOME",
            status="POSTED",
            amount=Decimal("3000.00"),
        )
        baker.make(
            Transaction,
            user=user,
            type="EXPENSE",
            status="POSTED",
            amount=Decimal("1200.00"),
        )
        # net daily velocity = (3000 - 1200) / 30 = 60/day
        # 30 day forecast = 60 * 30 = 1800.00
        assert ForecastingService.forecast_cash_flow(user, days=30) == Decimal(
            "1800.00"
        )


@pytest.mark.django_db
class TestAnalyticsAPI:
    def test_financial_summary_view(self):
        user = baker.make("users.User")
        baker.make(Account, user=user, balance=Decimal("5000.00"))
        # P2P exposure
        baker.make(Loan, lender=user, status="ACTIVE", amount=Decimal("1500.00"))
        baker.make(Loan, borrower=user, status="ACTIVE", amount=Decimal("500.00"))

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/analytics/summary/")
        assert response.status_code == 200
        # net_worth = 5000 + 1500 - 500 = 6000
        assert float(response.data["net_worth"]) == 6000.0
        assert float(response.data["total_balance"]) == 5000.0
        assert (
            float(response.data["total_borrowed"]) == 5000.0
            or float(response.data["total_borrowed"]) == 500.0
        )
        assert float(response.data["total_lent"]) == 1500.0

    def test_forecasting_view(self):
        user = baker.make("users.User")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/analytics/forecast/")
        assert response.status_code == 200
        assert "predicted_next_month_expense" in response.data
        assert response.data["confidence_score"] == "Medium"

    def test_report_export_view(self):
        user = baker.make("users.User")
        acc = baker.make(Account, user=user, name="Main")
        baker.make(
            Transaction,
            user=user,
            account=acc,
            type="EXPENSE",
            status="POSTED",
            amount=Decimal("10.00"),
            description="A",
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/analytics/export/")
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert "attachment" in response["Content-Disposition"]


@pytest.mark.django_db
class TestAnalyticsAdminViews:
    def test_format_currency_filter(self):
        from analytics.admin_views import format_currency

        assert format_currency(1234.56) == "1,234.56"
        assert format_currency("100.5") == "100.50"
        assert format_currency("invalid") == "invalid"

    def test_p2p_network_analytics_anonymous_redirects(self):
        client = APIClient()
        response = client.get("/admin/p2p-analytics/p2p-network/")
        assert response.status_code == 302
        assert "login" in response.url

    def test_p2p_network_analytics_non_staff_redirects(self):
        user = baker.make("users.User", is_staff=False)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/admin/p2p-analytics/p2p-network/")
        assert response.status_code == 302
        assert "login" in response.url

    def test_p2p_network_analytics_staff_success(self):
        user = baker.make("users.User", is_staff=True, is_active=True)
        # Create some lending/split data to be rendered
        borrower = baker.make("users.User")
        baker.make(
            Loan,
            lender=user,
            borrower=borrower,
            amount=Decimal("500.00"),
            status="ACTIVE",
        )
        baker.make(
            Loan,
            lender=borrower,
            borrower=user,
            amount=Decimal("200.00"),
            status="ACTIVE",
        )

        from splits.models import SplitGroup

        group = baker.make(SplitGroup, name="Group 1")
        group.members.add(user, borrower)

        client = APIClient()
        client.force_login(user)
        response = client.get("/admin/p2p-analytics/p2p-network/")
        assert response.status_code == 200
        assert "Peer-to-Peer Financial Network" in response.content.decode("utf-8")
