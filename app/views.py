from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connections
from django.core.cache import cache

class HealthCheckView(APIView):
    """
    Industry-standard health check endpoint for Kubernetes Liveness/Readiness probes.
    Verifies database and cache connectivity.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        health = {
            "status": "healthy",
            "services": {
                "database": "up",
                "cache": "up"
            }
        }
        
        # Check Database
        try:
            for conn in connections.all():
                conn.cursor()
        except Exception as e:
            health["status"] = "unhealthy"
            health["services"]["database"] = f"down: {str(e)}"
            
        # Check Cache (Redis)
        try:
            cache.set("health_check", "ok", timeout=5)
            if not cache.get("health_check"):
                raise ValueError("Cache read failed")
        except Exception as e:
            health["status"] = "unhealthy"
            health["services"]["cache"] = f"down: {str(e)}"
            
        status_code = status.HTTP_200_OK if health["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(health, status=status_code)
