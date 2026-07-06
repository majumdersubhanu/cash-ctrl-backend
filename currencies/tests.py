from decimal import Decimal
import pytest
from model_bakery import baker
from currencies.models import ExchangeRate
from currencies.services import CurrencyService


@pytest.mark.django_db
class TestExchangeRateAndCurrencyService:
    def test_exchange_rate_str(self):
        rate = baker.make(
            ExchangeRate,
            base_currency="USD",
            target_currency="EUR",
            rate=Decimal("0.85"),
        )
        assert str(rate) == "1 USD = 0.85 EUR"

    def test_get_rate_same_currency(self):
        assert ExchangeRate.get_rate("USD", "USD") == 1.0

    def test_get_rate_direct(self):
        baker.make(
            ExchangeRate,
            base_currency="USD",
            target_currency="EUR",
            rate=Decimal("0.85"),
        )
        assert ExchangeRate.get_rate("USD", "EUR") == Decimal("0.85")

    def test_get_rate_inverse(self):
        baker.make(
            ExchangeRate,
            base_currency="USD",
            target_currency="EUR",
            rate=Decimal("0.80"),
        )
        # 1 / 0.8 = 1.25
        assert float(ExchangeRate.get_rate("EUR", "USD")) == 1.25

    def test_get_rate_not_found(self):
        assert ExchangeRate.get_rate("USD", "GBP") is None

    def test_convert_same_currency(self):
        assert CurrencyService.convert(100, "USD", "USD") == Decimal("100.00")

    def test_convert_direct(self):
        baker.make(
            ExchangeRate,
            base_currency="USD",
            target_currency="EUR",
            rate=Decimal("0.85"),
        )
        assert CurrencyService.convert(100, "USD", "EUR") == Decimal("85.00")

    def test_convert_no_rate_raises_value_error(self):
        with pytest.raises(ValueError):
            CurrencyService.convert(100, "USD", "JPY")

    def test_update_rate_create(self):
        rate_obj = CurrencyService.update_rate(
            "USD", "GBP", Decimal("0.75"), "provider_x"
        )
        assert rate_obj.rate == Decimal("0.75")
        assert rate_obj.provider == "provider_x"
        assert ExchangeRate.objects.filter(
            base_currency="USD", target_currency="GBP"
        ).exists()

    def test_update_rate_update(self):
        baker.make(
            ExchangeRate,
            base_currency="USD",
            target_currency="GBP",
            rate=Decimal("0.70"),
        )
        rate_obj = CurrencyService.update_rate("USD", "GBP", Decimal("0.75"))
        assert rate_obj.rate == Decimal("0.75")
        assert ExchangeRate.objects.get(
            base_currency="USD", target_currency="GBP"
        ).rate == Decimal("0.75")


@pytest.mark.django_db
class TestExchangeRateAPI:
    def test_list_rates_authenticated(self):
        from rest_framework.test import APIClient

        user = baker.make("users.User")
        baker.make(
            ExchangeRate,
            base_currency="USD",
            target_currency="EUR",
            rate=Decimal("0.85"),
        )
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/currencies/rates/")
        assert response.status_code == 200
        assert len(response.data) == 1

    def test_list_rates_unauthenticated(self):
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.get("/api/v1/currencies/rates/")
        assert response.status_code == 401

    def test_create_rate_as_regular_user_returns_403(self):
        from rest_framework.test import APIClient

        user = baker.make("users.User")
        client = APIClient()
        client.force_authenticate(user=user)
        data = {"base_currency": "USD", "target_currency": "EUR", "rate": "0.85"}
        response = client.post("/api/v1/currencies/rates/", data, format="json")
        assert response.status_code == 403

    def test_create_rate_as_admin_user_success(self):
        from rest_framework.test import APIClient

        admin = baker.make("users.User", is_staff=True)
        client = APIClient()
        client.force_authenticate(user=admin)
        data = {"base_currency": "USD", "target_currency": "GBP", "rate": "0.72"}
        response = client.post("/api/v1/currencies/rates/", data, format="json")
        assert response.status_code == 201
        assert response.data["rate"] == "0.720000"
