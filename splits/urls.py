from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SplitGroupViewSet

router = DefaultRouter()
router.register(r"groups", SplitGroupViewSet, basename="splitgroup")

urlpatterns = [
    path("", include(router.urls)),
]
