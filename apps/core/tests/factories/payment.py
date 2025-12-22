import factory

from apps.core.tests.factories.loan import LoanFactory
from apps.payments.models import Payment
from credit_track.test_settings import FAKER_GENERATOR


class PaymentFactory(factory.django.DjangoModelFactory):
    """Factory for creating Payment instances."""

    loan = factory.SubFactory(LoanFactory)
    payment_date = factory.LazyAttribute(
        lambda obj: FAKER_GENERATOR.date_between(
            start_date=obj.loan.request_date, end_date="today"
        )
    )
    payment_value = factory.LazyAttribute(
        lambda payment_value: FAKER_GENERATOR.pydecimal(
            left_digits=5,
            right_digits=2,
            positive=True,
            min_value=100,
            max_value=50000,
        )
    )

    # Audit fields (optional - can be set explicitly in tests)
    created_by = factory.LazyAttribute(lambda obj: obj.loan.owner)
    updated_by = factory.LazyAttribute(lambda obj: obj.loan.owner)

    class Meta:
        model = Payment
