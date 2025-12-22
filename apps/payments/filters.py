import django_filters
from django.db import models

from apps.payments.models import Payment


class PaymentFilter(django_filters.FilterSet):
    """Filtros para o endpoint de pagamentos."""

    # Filtro por empréstimo
    loan = django_filters.UUIDFilter(field_name="loan__uuid")

    # Filtros de data
    payment_date = django_filters.DateFilter(field_name="payment_date")
    payment_date__gte = django_filters.DateFilter(
        field_name="payment_date", lookup_expr="gte"
    )
    payment_date__lte = django_filters.DateFilter(
        field_name="payment_date", lookup_expr="lte"
    )
    payment_date__year = django_filters.NumberFilter(
        field_name="payment_date", lookup_expr="year"
    )
    payment_date__month = django_filters.NumberFilter(
        field_name="payment_date", lookup_expr="month"
    )

    # Filtros de valor
    payment_value = django_filters.NumberFilter(field_name="payment_value")
    payment_value__gte = django_filters.NumberFilter(
        field_name="payment_value", lookup_expr="gte"
    )
    payment_value__lte = django_filters.NumberFilter(
        field_name="payment_value", lookup_expr="lte"
    )

    # Filtro de busca geral
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        """Busca em múltiplos campos."""
        return queryset.filter(
            models.Q(uuid__icontains=value)
            | models.Q(loan__uuid__icontains=value)
        )

    class Meta:
        model = Payment
        fields = [
            "loan",
            "payment_date",
            "payment_value",
        ]
