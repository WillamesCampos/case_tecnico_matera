from decimal import Decimal

import pytest

from apps.loans.services.interest_calculator_svc import (
    InterestCalculatorService,
)


@pytest.fixture
def interest_calculator():
    """Fixture for InterestCalculatorService."""
    return InterestCalculatorService()


@pytest.mark.django_db
def test_calculate_compound_interest_one_month(interest_calculator):
    """Test compound interest calculation for 1 month."""
    # Arrange
    loan_amount = Decimal("10000.00")
    rate_percent = Decimal("2.5")
    months = 1

    # Act
    result = interest_calculator.calculate_compound_interest(
        loan_amount, rate_percent, months
    )

    # Assert
    expected = Decimal("10000.00") * (Decimal("1") + Decimal("0.025")) ** 1
    assert result == expected
    assert result == Decimal("10250.00")


@pytest.mark.django_db
def test_calculate_compound_interest_multiple_months(interest_calculator):
    """Test compound interest calculation for multiple months."""
    # Arrange
    loan_amount = Decimal("10000.00")
    rate_percent = Decimal("2.5")
    months = 3

    # Act
    result = interest_calculator.calculate_compound_interest(
        loan_amount, rate_percent, months
    )

    # Assert
    expected = Decimal("10000.00") * (Decimal("1") + Decimal("0.025")) ** 3
    assert result == expected


@pytest.mark.django_db
def test_calculate_compound_interest_zero_months(interest_calculator):
    """Test compound interest calculation for 0 months returns principal."""
    # Arrange
    loan_amount = Decimal("10000.00")
    rate_percent = Decimal("2.5")
    months = 0

    # Act
    result = interest_calculator.calculate_compound_interest(
        loan_amount, rate_percent, months
    )

    # Assert
    assert result == loan_amount


@pytest.mark.django_db
def test_calculate_compound_interest_negative_months(interest_calculator):
    """Test compound interest calculation for negative months
    returns principal.
    """
    # Arrange
    loan_amount = Decimal("10000.00")
    rate_percent = Decimal("2.5")
    months = -1

    # Act
    result = interest_calculator.calculate_compound_interest(
        loan_amount, rate_percent, months
    )

    # Assert
    assert result == loan_amount


@pytest.mark.django_db
def test_calculate_compound_interest_zero_rate(interest_calculator):
    """Test compound interest calculation with zero interest rate."""
    # Arrange
    loan_amount = Decimal("10000.00")
    rate_percent = Decimal("0.00")
    months = 3

    # Act
    result = interest_calculator.calculate_compound_interest(
        loan_amount, rate_percent, months
    )

    # Assert
    assert result == loan_amount


@pytest.mark.django_db
def test_calculate_compound_interest_high_rate(interest_calculator):
    """Test compound interest calculation with high interest rate."""
    # Arrange
    loan_amount = Decimal("10000.00")
    rate_percent = Decimal("10.00")
    months = 2

    # Act
    result = interest_calculator.calculate_compound_interest(
        loan_amount, rate_percent, months
    )

    # Assert
    expected = Decimal("10000.00") * (Decimal("1") + Decimal("0.10")) ** 2
    assert result == expected
    assert result == Decimal("12100.00")
