from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.payments.models import Payment


@pytest.mark.django_db
def test_payment_value_cannot_be_zero():
    """Test that payment value cannot be 0."""
    # Arrange
    loan = LoanFactory()

    # Act & Assert
    with pytest.raises(IntegrityError):
        Payment.objects.create(
            loan=loan,
            payment_date=loan.request_date,
            payment_value=Decimal("0.00"),
        )


@pytest.mark.django_db
def test_payment_value_cannot_be_negative():
    """Test that payment value cannot be negative."""
    # Arrange
    loan = LoanFactory()

    # Act & Assert
    with pytest.raises(IntegrityError):
        Payment.objects.create(
            loan=loan,
            payment_date=loan.request_date,
            payment_value=Decimal("-100.00"),
        )


@pytest.mark.django_db
def test_payment_value_can_be_positive():
    """Test that payment value can be positive."""
    # Arrange
    loan = LoanFactory()

    # Act
    payment = PaymentFactory(loan=loan, payment_value=Decimal("100.00"))

    # Assert
    assert payment.payment_value > 0
