import pytest
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker


@pytest.mark.django_db
class TestHealthCheckView:
    def test_health_check_healthy(self):
        client = APIClient()
        response = client.get("/health/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "healthy"
        assert response.data["services"]["database"] == "up"
        assert response.data["services"]["cache"] == "up"

    @patch("django.db.connections.all")
    def test_health_check_db_unhealthy(self, mock_connections_all):
        from unittest.mock import MagicMock

        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("DB Connection Refused")
        mock_connections_all.return_value = [mock_conn]

        client = APIClient()
        response = client.get("/health/")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data["status"] == "unhealthy"
        assert "down" in response.data["services"]["database"]

    @patch("django.core.cache.cache.set")
    def test_health_check_cache_unhealthy(self, mock_cache_set):
        def side_effect(key, value, timeout=None):
            if key == "health_check":
                raise Exception("Redis connection down")
            return None

        mock_cache_set.side_effect = side_effect

        client = APIClient()
        response = client.get("/health/")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data["status"] == "unhealthy"
        assert "down" in response.data["services"]["cache"]

    @patch("django.core.cache.cache.get")
    def test_health_check_cache_read_failure(self, mock_cache_get):
        def side_effect(key, default=None):
            if key == "health_check":
                return None
            return default if default is not None else []

        mock_cache_get.side_effect = side_effect

        client = APIClient()
        response = client.get("/health/")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.data["status"] == "unhealthy"
        assert "down: Cache read failed" in response.data["services"]["cache"]


class TestSchemaHooks:
    def test_custom_postprocessing_hook(self):
        from app.schema_hooks import custom_postprocessing_hook

        result = {
            "paths": {
                "/api/v1/auth/login/": {
                    "post": {"operationId": "api_v1_auth_login_create"}
                },
                "/api/v1/some/other/path/": {
                    "get": {"operationId": "api_v1_some_other_retrieve"}
                },
                "/api/v1/register/": {"post": {"operationId": "registration_create"}},
                "/api/v1/auth/password_reset/": {
                    "post": {"operationId": "api_v1_auth_password_reset_create"}
                },
                "/api/v1/auth/password_reset_confirm/": {
                    "post": {"operationId": "api_v1_auth_password_reset_confirm_create"}
                },
                "/api/v1/auth/logout/": {
                    "post": {"operationId": "api_v1_auth_logout_create"}
                },
                "/api/v1/users/me/": {
                    "get": {"operationId": "api_v1_users_user_retrieve"},
                    "put": {"operationId": "api_v1_users_user_update"},
                },
                "/api/v1/users/phone/request_otp/": {
                    "post": {"operationId": "api_v1_users_phone_request_otp_create"}
                },
                "/api/v1/users/phone/verify_otp/": {
                    "post": {"operationId": "api_v1_users_phone_verify_otp_create"}
                },
                "/api/v1/register/verify_email/": {
                    "post": {"operationId": "registration_verify_email_create"}
                },
            }
        }

        updated = custom_postprocessing_hook(result, None)
        assert updated["paths"]["/api/v1/auth/login/"]["post"]["operationId"] == "login"
        assert updated["paths"]["/api/v1/auth/login/"]["post"]["tags"] == [
            "Authentication"
        ]
        assert updated["paths"]["/api/v1/register/"]["post"]["tags"] == [
            "Authentication"
        ]
        assert (
            updated["paths"]["/api/v1/register/"]["post"]["operationId"]
            == "register_alt"
        )
        assert (
            updated["paths"]["/api/v1/auth/password_reset/"]["post"]["operationId"]
            == "password_reset"
        )
        assert (
            updated["paths"]["/api/v1/auth/password_reset_confirm/"]["post"][
                "operationId"
            ]
            == "password_reset_confirm"
        )
        assert (
            updated["paths"]["/api/v1/auth/logout/"]["post"]["operationId"] == "logout"
        )
        assert updated["paths"]["/api/v1/users/me/"]["get"]["operationId"] == "get_user"
        assert (
            updated["paths"]["/api/v1/users/me/"]["put"]["operationId"] == "update_user"
        )
        assert (
            updated["paths"]["/api/v1/users/phone/request_otp/"]["post"]["operationId"]
            == "request_otp"
        )
        assert (
            updated["paths"]["/api/v1/users/phone/verify_otp/"]["post"]["operationId"]
            == "verify_otp"
        )
        assert (
            updated["paths"]["/api/v1/register/verify_email/"]["post"]["operationId"]
            == "verify_email"
        )

    def test_custom_preprocessing_hook(self):
        from app.schema_hooks import custom_preprocessing_hook

        endpoints = [
            ("/api/v1/auth/login/", None, "POST", None),
            ("/api/v1/users/", None, "GET", None),
        ]
        res = custom_preprocessing_hook(endpoints)
        assert len(res) == 2
        assert res[0][0] == "/api/v1/auth/login/"


@pytest.mark.django_db
class TestMiddleware:
    @patch("app.middleware.logger")
    def test_performance_middleware_slow_request(self, mock_logger):
        from app.middleware import PerformanceMiddleware
        from django.http import HttpResponse

        def dummy_get_response(request):
            import time

            time.sleep(0.6)  # simulate slow request
            return HttpResponse("OK")

        middleware = PerformanceMiddleware(dummy_get_response)

        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/health/")

        # mock user
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()

        response = middleware(request)
        assert response.status_code == 200
        assert mock_logger.warning.called


@pytest.mark.django_db
class TestDashboard:
    def test_custom_index_dashboard(self):
        from app.dashboard import CustomIndexDashboard

        class MockIndexDashboard(CustomIndexDashboard):
            def __init__(self, context):
                self.children = []
                self.context = context

        # mock context with Request
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/admin/")

        # create mock users/objects to check queries inside init_with_context
        from django.contrib.auth import get_user_model

        User = get_user_model()
        baker.make(User)

        context = {"request": request}
        dashboard = MockIndexDashboard(context)
        dashboard.init_with_context(context)
        assert len(dashboard.children) > 0

    def test_custom_app_index_dashboard(self):
        from app.dashboard import CustomAppIndexDashboard

        class MockDashboard(CustomAppIndexDashboard):
            def __init__(self, context):
                self.children = []
                self.context = context

            def models(self):
                return []

            def get_app_content_types(self):
                return []

        # mock context with Request
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/admin/")
        context = {"request": request}

        dashboard = MockDashboard(context)
        dashboard.init_with_context(context)
        assert len(dashboard.children) > 0


def test_celery_debug_task():
    from app.celery import debug_task

    debug_task.apply()
