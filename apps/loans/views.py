from rest_framework import viewsets

from apps.loans.models import Loan
from apps.loans.serializers import LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
