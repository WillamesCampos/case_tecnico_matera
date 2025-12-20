from rest_framework import viewsets

from apps.loans.models import Loan
from apps.loans.serializers import LoanListSerializer, LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        """Filter loans to only show those owned by the authenticated user."""
        return Loan.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return LoanListSerializer
        return LoanSerializer
