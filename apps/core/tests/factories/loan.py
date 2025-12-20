import factory

from apps.core.tests.factories.user import UserFactory
from apps.loans.models import Loan
from credit_track.test_settings import FAKER_GENERATOR


class LoanFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    bank = factory.LazyAttribute(lambda obj: FAKER_GENERATOR.company())
    amount = factory.LazyAttribute(
        lambda obj: FAKER_GENERATOR.pydecimal(
            left_digits=6,
            right_digits=2,
            positive=True,
            min_value=1000,
            max_value=1000000,
        )
    )
    interest_rate = factory.LazyAttribute(
        lambda obj: FAKER_GENERATOR.pydecimal(
            left_digits=2,
            right_digits=2,
            positive=True,
            min_value=0.5,
            max_value=16.0,
        )
    )
    request_date = factory.LazyAttribute(
        lambda request_date: FAKER_GENERATOR.date_between(
            start_date="-1y", end_date="today"
        )
    )
    request_ip = factory.LazyAttribute(
        lambda request_ip: FAKER_GENERATOR.ipv4()
    )
    created_by = factory.LazyAttribute(lambda obj: obj.owner)
    updated_by = factory.LazyAttribute(lambda obj: obj.owner)

    class Meta:
        model = Loan
