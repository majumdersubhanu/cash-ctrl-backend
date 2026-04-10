from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegistrationView, MeView, PhoneAuthViewSet, GoogleLogin

router = DefaultRouter()
router.register(r"phone", PhoneAuthViewSet, basename="phone-auth")

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("", include(router.urls)),
]
