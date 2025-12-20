"""
Factories for creating test data using factory_boy and faker.
"""

import factory
from django.contrib.auth import get_user_model
from faker import Faker

from apps.loans.models import Loan
from apps.payments.models import Payment

User = get_user_model()
fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        password = extracted or "testpass123"
        self.set_password(password)
        self.save()


class LoanFactory(factory.django.DjangoModelFactory):
    """Factory for creating Loan instances."""

    class Meta:
        model = Loan

    owner = factory.SubFactory(UserFactory)
    bank = factory.Faker("company")
    amount = factory.Faker(
        "pydecimal",
        left_digits=6,
        right_digits=2,
        positive=True,
        min_value=1000,
        max_value=1000000,
    )
    interest_rate = factory.Faker(
        "pydecimal",
        left_digits=2,
        right_digits=2,
        positive=True,
        min_value=0.5,
        max_value=10.0,
    )
    request_date = factory.Faker(
        "date_between", start_date="-1y", end_date="today"
    )
    request_ip = factory.Faker("ipv4")

    # Audit fields (optional - can be set explicitly in tests)
    created_by = factory.LazyAttribute(lambda obj: obj.owner)
    updated_by = factory.LazyAttribute(lambda obj: obj.owner)


class PaymentFactory(factory.django.DjangoModelFactory):
    """Factory for creating Payment instances."""

    class Meta:
        model = Payment

    loan = factory.SubFactory(LoanFactory)
    payment_date = factory.LazyAttribute(
        lambda obj: fake.date_between(
            start_date=obj.loan.request_date, end_date="today"
        )
    )
    payment_value = factory.Faker(
        "pydecimal",
        left_digits=5,
        right_digits=2,
        positive=True,
        min_value=100,
        max_value=50000,
    )

    # Audit fields (optional - can be set explicitly in tests)
    created_by = factory.LazyAttribute(lambda obj: obj.loan.owner)
    updated_by = factory.LazyAttribute(lambda obj: obj.loan.owner)

    @factory.post_generation
    def ensure_payment_date_after_loan(self, create, extracted, **kwargs):
        """Ensure payment_date is not before loan.request_date."""
        if create and self.payment_date < self.loan.request_date:
            self.payment_date = self.loan.request_date
            self.save()
