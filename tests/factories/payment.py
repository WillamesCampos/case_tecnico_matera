import factory

from apps.payments.models import Payment
from credit_track.test_settings import FAKER_GENERATOR
from tests.factories.loan import LoanFactory


class PaymentFactory(factory.django.DjangoModelFactory):
    """Factory for creating Payment instances."""

    loan = factory.SubFactory(LoanFactory)
    payment_date = factory.LazyAttribute(
        lambda payment_date: FAKER_GENERATOR.date_between(
            start_date=payment_date.loan.request_date, end_date="today"
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
    created_by = factory.LazyAttribute(
        lambda created_by: created_by.loan.owner
    )
    updated_by = factory.LazyAttribute(
        lambda updated_by: updated_by.loan.owner
    )

    @factory.post_generation
    def ensure_payment_date_after_loan(self, create, extracted, **kwargs):
        """Ensure payment_date is not before loan.request_date."""
        if create and self.payment_date < self.loan.request_date:
            self.payment_date = self.loan.request_date
            self.save()

    class Meta:
        model = Payment
