from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError

from apps.core.tests.factories.loan import LoanFactory
from apps.loans.services.payment_validator_svc import PaymentValidatorService


@pytest.fixture
def payment_validator():
    """Fixture for PaymentValidatorService."""
    return PaymentValidatorService()


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_validate_payment_success(payment_validator):
    """Test that valid payment passes validation."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    payment_date = date(2024, 2, 15)
    payment_value = Decimal("1000.00")

    # Mock outstanding balance calculator
    mock_calculator = MagicMock()
    mock_calculator.calculate.return_value = Decimal("5000.00")
    payment_validator.outstanding_balance_calculator = mock_calculator

    # Act & Assert
    # Should not raise
    payment_validator.validate_payment(payment_date, payment_value, loan)


@pytest.mark.django_db
def test_validate_payment_date_before_loan_date_raises_error(
    payment_validator,
):
    """Test that payment date before loan request date raises error."""
    # Arrange
    loan = LoanFactory(request_date=date(2024, 2, 1))
    payment_date = date(2024, 1, 15)
    payment_value = Decimal("1000.00")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        payment_validator.validate_payment(payment_date, payment_value, loan)

    assert "payment_date" in str(exc_info.value)
    assert "cannot be before" in str(exc_info.value)


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_validate_payment_date_future_raises_error(payment_validator):
    """Test that payment date in the future raises error."""
    # Arrange
    loan = LoanFactory(request_date=date(2024, 1, 1))
    payment_date = date(2024, 3, 15)  # Future date
    payment_value = Decimal("1000.00")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        payment_validator.validate_payment(payment_date, payment_value, loan)

    assert "payment_date" in str(exc_info.value)
    assert "cannot be in the future" in str(exc_info.value)


@pytest.mark.django_db
def test_validate_payment_value_zero_raises_error(payment_validator):
    """Test that payment value of zero raises error."""
    # Arrange
    loan = LoanFactory()
    payment_date = loan.request_date
    payment_value = Decimal("0.00")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        payment_validator.validate_payment(payment_date, payment_value, loan)

    assert "payment_value" in str(exc_info.value)
    assert "greater than 0" in str(exc_info.value)


@pytest.mark.django_db
def test_validate_payment_value_negative_raises_error(payment_validator):
    """Test that negative payment value raises error."""
    # Arrange
    loan = LoanFactory()
    payment_date = loan.request_date
    payment_value = Decimal("-100.00")

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        payment_validator.validate_payment(payment_date, payment_value, loan)

    assert "payment_value" in str(exc_info.value)
    assert "greater than 0" in str(exc_info.value)


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_validate_payment_value_exceeds_outstanding_balance_raises_error(
    payment_validator,
):
    """Test that payment value exceeding outstanding balance raises error."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    payment_date = date(2024, 2, 15)
    payment_value = Decimal("20000.00")  # Exceeds outstanding balance

    # Mock outstanding balance calculator
    mock_calculator = MagicMock()
    mock_calculator.calculate.return_value = Decimal("5000.00")
    payment_validator.outstanding_balance_calculator = mock_calculator

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        payment_validator.validate_payment(payment_date, payment_value, loan)

    assert "payment_value" in str(exc_info.value)
    assert "cannot exceed" in str(exc_info.value)
    mock_calculator.calculate.assert_called_once_with(loan)


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_validate_payment_value_equals_outstanding_balance_success(
    payment_validator,
):
    """Test that payment value equal to outstanding balance passes."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    payment_date = date(2024, 2, 15)
    payment_value = Decimal("5000.00")

    # Mock outstanding balance calculator
    mock_calculator = MagicMock()
    mock_calculator.calculate.return_value = Decimal("5000.00")
    payment_validator.outstanding_balance_calculator = mock_calculator

    # Act & Assert
    # Should not raise
    payment_validator.validate_payment(payment_date, payment_value, loan)
