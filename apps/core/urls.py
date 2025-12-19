from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.core.views import HealthCheckView

urlpatterns = [
    path("health-check/", HealthCheckView.as_view(), name="health-check"),
    path(
        "auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"
    ),
    path(
        "auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"
    ),
]
