import django_filters
from django.db import models

from apps.loans.models import Loan


class LoanFilter(django_filters.FilterSet):
    """Filtros para o endpoint de empréstimos."""

    # Filtros de data
    request_date = django_filters.DateFilter(field_name="request_date")
    request_date__gte = django_filters.DateFilter(
        field_name="request_date", lookup_expr="gte"
    )
    request_date__lte = django_filters.DateFilter(
        field_name="request_date", lookup_expr="lte"
    )
    request_date__year = django_filters.NumberFilter(
        field_name="request_date", lookup_expr="year"
    )
    request_date__month = django_filters.NumberFilter(
        field_name="request_date", lookup_expr="month"
    )

    # Filtros de valor
    amount = django_filters.NumberFilter(field_name="amount")
    amount__gte = django_filters.NumberFilter(
        field_name="amount", lookup_expr="gte"
    )
    amount__lte = django_filters.NumberFilter(
        field_name="amount", lookup_expr="lte"
    )

    # Filtros de taxa de juros
    interest_rate = django_filters.NumberFilter(field_name="interest_rate")
    interest_rate__gte = django_filters.NumberFilter(
        field_name="interest_rate", lookup_expr="gte"
    )
    interest_rate__lte = django_filters.NumberFilter(
        field_name="interest_rate", lookup_expr="lte"
    )

    # Filtro de banco (busca parcial)
    bank = django_filters.CharFilter(
        field_name="bank", lookup_expr="icontains"
    )

    # Filtro de busca geral
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        """Busca em múltiplos campos."""
        return queryset.filter(
            models.Q(bank__icontains=value) | models.Q(uuid__icontains=value)
        )

    class Meta:
        model = Loan
        fields = [
            "request_date",
            "amount",
            "interest_rate",
            "bank",
        ]
