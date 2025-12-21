from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time

from apps.core.tests.factories.loan import LoanFactory
from apps.loans.services.outstanding_balance_calculator_svc import (
    OutstandingBalanceCalculatorService,
)
from apps.loans.use_cases.calculate_loan_outstanding_balance_use_case import (
    CalculateLoanOutstandingBalanceUseCase,
)


@pytest.fixture
def use_case():
    """Fixture for CalculateLoanOutstandingBalanceUseCase."""
    return CalculateLoanOutstandingBalanceUseCase()


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_execute_calls_calculator_with_loan(use_case):
    """Test that execute calls the calculator service with loan."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    mock_calculator = MagicMock(spec=OutstandingBalanceCalculatorService)
    mock_calculator.calculate.return_value = Decimal("10506.25")
    use_case.outstanding_balance_calculator = mock_calculator

    # Act
    result = use_case.execute(loan)

    # Assert
    assert result == Decimal("10506.25")
    mock_calculator.calculate.assert_called_once_with(loan, None)


@pytest.mark.django_db
def test_execute_calls_calculator_with_reference_date(use_case):
    """Test that execute calls the calculator service with reference date."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    reference_date = date(2024, 4, 1)
    mock_calculator = MagicMock(spec=OutstandingBalanceCalculatorService)
    mock_calculator.calculate.return_value = Decimal("10768.91")
    use_case.outstanding_balance_calculator = mock_calculator

    # Act
    result = use_case.execute(loan, reference_date)

    # Assert
    assert result == Decimal("10768.91")
    mock_calculator.calculate.assert_called_once_with(loan, reference_date)


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_execute_returns_calculator_result(use_case):
    """Test that execute returns the result from calculator service."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )

    # Act
    result = use_case.execute(loan)

    # Assert
    # Should calculate correctly:
    # (10000 * (1.025)^2) + IOF = 10506.25 + 87.20 = 10593.45
    # IOF: Fixed (38.00) + Daily (60 days * 0.0082% = 49.20) = 87.20
    amount_with_interest = (
        Decimal("10000.00") * (Decimal("1") + Decimal("0.025")) ** 2
    )
    iof_fixed = Decimal("10000.00") * Decimal("0.0038")  # 38.00
    iof_daily = (
        Decimal("10000.00") * Decimal("0.000082") * Decimal("60")
    )  # 49.20
    total_iof = iof_fixed + iof_daily
    expected = amount_with_interest + total_iof
    assert result == expected
