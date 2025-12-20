from rest_framework import viewsets

from apps.payments.models import Payment
from apps.payments.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(loan__owner=self.request.user)
