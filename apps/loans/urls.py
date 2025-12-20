from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.loans.views import LoanViewSet

router = DefaultRouter()
router.register(r"loans", LoanViewSet, basename="loan")


urlpatterns = [
    path("", include(router.urls)),
]
