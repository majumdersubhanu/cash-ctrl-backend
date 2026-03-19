import logging
import time

from django.db import connection

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log if request takes more than 500ms
        if duration > 0.5:
            logger.warning(
                f"Slow Request: {request.method} {request.path} "
                f"took {duration:.2f}s (User: {request.user})"
            )

        return response


class RLSMiddleware:
    """
    Injects the authenticated user's ID into the PostgreSQL transaction context
    for Row-Level Security evaluation.
    Requires ATOMIC_REQUESTS = True to persist the SET LOCAL across the request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL app.current_user_id = %s;", [request.user.id])
        else:
            with connection.cursor() as cursor:
                cursor.execute("SET LOCAL app.current_user_id = '';")

        return self.get_response(request)
