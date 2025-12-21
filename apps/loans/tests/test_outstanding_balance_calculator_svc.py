from datetime import date
from decimal import Decimal

import pytest
from freezegun import freeze_time

from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.loans.services.outstanding_balance_calculator_svc import (
    OutstandingBalanceCalculatorService,
)


@pytest.fixture
def outstanding_balance_calculator():
    """Fixture for OutstandingBalanceCalculatorService."""
    return OutstandingBalanceCalculatorService()


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_calculate_outstanding_balance_no_payments(
    outstanding_balance_calculator,
):
    """Test outstanding balance calculation with no payments."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )

    # Act
    result = outstanding_balance_calculator.calculate(loan)

    # Assert
    # 2 months of interest: 10000 * (1.025)^2 = 10506.25
    expected = Decimal("10000.00") * (Decimal("1") + Decimal("0.025")) ** 2
    assert result == expected
    assert result == Decimal("10506.25")


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_calculate_outstanding_balance_with_payments(
    outstanding_balance_calculator,
):
    """Test outstanding balance calculation with payments."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    PaymentFactory(loan=loan, payment_value=Decimal("2000.00"))

    # Act
    result = outstanding_balance_calculator.calculate(loan)

    # Assert
    # Amount with interest: 10000 * (1.025)^2 = 10506.25
    # Total paid: 2000.00
    # Outstanding: 10506.25 - 2000.00 = 8506.25
    amount_with_interest = (
        Decimal("10000.00") * (Decimal("1") + Decimal("0.025")) ** 2
    )
    expected = amount_with_interest - Decimal("2000.00")
    assert result == expected
    assert result == Decimal("8506.25")


@pytest.mark.django_db
@freeze_time("2024-03-01")
def test_calculate_outstanding_balance_overpayment_returns_zero(
    outstanding_balance_calculator,
):
    """Test that outstanding balance returns 0 when payments exceed balance."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    # Payment exceeds amount with interest
    PaymentFactory(loan=loan, payment_value=Decimal("20000.00"))

    # Act
    result = outstanding_balance_calculator.calculate(loan)

    # Assert
    assert result == Decimal("0.00")


@pytest.mark.django_db
@freeze_time("2024-01-15")
def test_calculate_outstanding_balance_same_month_returns_principal(
    outstanding_balance_calculator,
):
    """Test outstanding balance in the same month as request date."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )

    # Act
    result = outstanding_balance_calculator.calculate(loan)

    # Assert
    # Same month = 0 months, so no interest
    assert result == Decimal("10000.00")


@pytest.mark.django_db
def test_calculate_outstanding_balance_with_reference_date(
    outstanding_balance_calculator,
):
    """Test outstanding balance calculation with custom reference date."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        interest_rate=Decimal("2.5"),
        request_date=date(2024, 1, 1),
    )
    reference_date = date(2024, 4, 1)

    # Act
    result = outstanding_balance_calculator.calculate(loan, reference_date)

    # Assert
    # 3 months of interest: 10000 * (1.025)^3 = 10768.90625...
    expected = Decimal("10000.00") * (Decimal("1") + Decimal("0.025")) ** 3
    assert result == expected


@pytest.mark.django_db
def test_calculate_months_same_date_returns_zero(
    outstanding_balance_calculator,
):
    """Test _calculate_months returns 0 for same date."""
    # Arrange
    start_date = date(2024, 1, 15)
    end_date = date(2024, 1, 15)

    # Act
    result = outstanding_balance_calculator._calculate_months(
        start_date, end_date
    )

    # Assert
    assert result == 0


@pytest.mark.django_db
def test_calculate_months_one_month_difference(outstanding_balance_calculator):
    """Test _calculate_months for one month difference."""
    # Arrange
    start_date = date(2024, 1, 15)
    end_date = date(2024, 2, 15)

    # Act
    result = outstanding_balance_calculator._calculate_months(
        start_date, end_date
    )

    # Assert
    assert result == 1


@pytest.mark.django_db
def test_calculate_months_multiple_months_difference(
    outstanding_balance_calculator,
):
    """Test _calculate_months for multiple months difference."""
    # Arrange
    start_date = date(2024, 1, 15)
    end_date = date(2024, 4, 15)

    # Act
    result = outstanding_balance_calculator._calculate_months(
        start_date, end_date
    )

    # Assert
    assert result == 3


@pytest.mark.django_db
def test_calculate_months_end_before_start_returns_zero(
    outstanding_balance_calculator,
):
    """Test _calculate_months returns 0 when end_date is before start_date."""
    # Arrange
    start_date = date(2024, 2, 15)
    end_date = date(2024, 1, 15)

    # Act
    result = outstanding_balance_calculator._calculate_months(
        start_date, end_date
    )

    # Assert
    assert result == 0
