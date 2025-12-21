from decimal import Decimal

import pytest

from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.loans.services.payment_aggregator_svc import PaymentAggregatorService


@pytest.fixture
def payment_aggregator():
    """Fixture for PaymentAggregatorService."""
    return PaymentAggregatorService()


@pytest.mark.django_db
def test_get_total_paid_with_no_payments(payment_aggregator):
    """Test that get_total_paid returns 0 when loan has no payments."""
    # Arrange
    loan = LoanFactory()

    # Act
    result = payment_aggregator.get_total_paid(loan)

    # Assert
    assert result == Decimal("0.00")


@pytest.mark.django_db
def test_get_total_paid_with_single_payment(payment_aggregator):
    """Test that get_total_paid returns correct value for single payment."""
    # Arrange
    loan = LoanFactory()
    PaymentFactory(loan=loan, payment_value=Decimal("1000.00"))

    # Act
    result = payment_aggregator.get_total_paid(loan)

    # Assert
    assert result == Decimal("1000.00")


@pytest.mark.django_db
def test_get_total_paid_with_multiple_payments(payment_aggregator):
    """Test that get_total_paid sums multiple payments correctly."""
    # Arrange
    loan = LoanFactory()
    PaymentFactory(loan=loan, payment_value=Decimal("1000.00"))
    PaymentFactory(loan=loan, payment_value=Decimal("2000.00"))
    PaymentFactory(loan=loan, payment_value=Decimal("500.00"))

    # Act
    result = payment_aggregator.get_total_paid(loan)

    # Assert
    assert result == Decimal("3500.00")


@pytest.mark.django_db
def test_get_total_paid_with_decimal_precision(payment_aggregator):
    """Test that get_total_paid handles decimal precision correctly."""
    # Arrange
    loan = LoanFactory()
    PaymentFactory(loan=loan, payment_value=Decimal("1000.50"))
    PaymentFactory(loan=loan, payment_value=Decimal("2000.75"))

    # Act
    result = payment_aggregator.get_total_paid(loan)

    # Assert
    assert result == Decimal("3001.25")
