from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from rest_framework.exceptions import ValidationError

from apps.core.tests.factories.loan import LoanFactory
from apps.loans.services.payment_validator_svc import PaymentValidatorService
from apps.loans.use_cases.validate_payment_use_case import (
    ValidatePaymentUseCase,
)


@pytest.fixture
def use_case():
    """Fixture for ValidatePaymentUseCase."""
    return ValidatePaymentUseCase()


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_execute_calls_validator_with_correct_params(use_case):
    """Test that execute calls the validator service with
    correct parameters.
    """
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    payment_date = date(2024, 2, 15)
    payment_value = Decimal("1000.00")

    mock_validator = MagicMock(spec=PaymentValidatorService)
    use_case.payment_validator = mock_validator

    # Act
    use_case.execute(payment_date, payment_value, loan)

    # Assert
    mock_validator.validate_payment.assert_called_once_with(
        payment_date, payment_value, loan
    )


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_execute_raises_validation_error_when_validator_fails(use_case):
    """Test that execute raises ValidationError when validator fails."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    payment_date = date(2024, 2, 15)
    payment_value = Decimal("20000.00")  # Exceeds balance

    mock_validator = MagicMock(spec=PaymentValidatorService)
    mock_validator.validate_payment.side_effect = ValidationError(
        {"payment_value": "Cannot exceed outstanding balance"}
    )
    use_case.payment_validator = mock_validator

    # Act & Assert
    with pytest.raises(ValidationError):
        use_case.execute(payment_date, payment_value, loan)


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_execute_success_with_valid_payment(use_case):
    """Test that execute succeeds with valid payment."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    payment_date = date(2024, 2, 15)
    payment_value = Decimal("1000.00")

    # Act & Assert
    # Should not raise
    use_case.execute(payment_date, payment_value, loan)
