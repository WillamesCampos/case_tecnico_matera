from datetime import date
from decimal import Decimal

import pytest
from freezegun import freeze_time

from apps.core.tests.factories.loan import LoanFactory
from apps.loans.services.iof_calculator_svc import IOFCalculatorService


@pytest.fixture
def iof_calculator():
    """Fixture for IOFCalculatorService."""
    return IOFCalculatorService()


@pytest.mark.django_db
def test_calculate_fixed_iof(iof_calculator):
    """Test fixed IOF calculation (0.38% of loan amount)."""
    # Arrange
    loan_amount = Decimal("10000.00")

    # Act
    result = iof_calculator.calculate_fixed_iof(loan_amount)

    # Assert
    expected = loan_amount * Decimal("0.0038")
    assert result == expected
    assert result == Decimal("38.00")


@pytest.mark.django_db
def test_calculate_fixed_iof_different_amount(iof_calculator):
    """Test fixed IOF calculation with different amount."""
    # Arrange
    loan_amount = Decimal("5000.00")

    # Act
    result = iof_calculator.calculate_fixed_iof(loan_amount)

    # Assert
    expected = loan_amount * Decimal("0.0038")
    assert result == expected
    assert result == Decimal("19.00")


@pytest.mark.django_db
@freeze_time("2024-07-01")
def test_calculate_daily_iof_30_days(iof_calculator):
    """Test daily IOF calculation for 30 days."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 6, 1),
    )

    # Act
    result = iof_calculator.calculate_daily_iof(loan)

    # Assert
    # 30 days * 0.0082% = 0.246% of 10000 = 24.60
    expected = Decimal("10000.00") * Decimal("0.000082") * Decimal("30")
    assert result == expected
    assert result == Decimal("24.60")


@pytest.mark.django_db
@freeze_time("2024-06-29")
def test_calculate_daily_iof_180_days(iof_calculator):
    """Test daily IOF calculation for 180 days."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 1, 1),
    )

    # Act
    result = iof_calculator.calculate_daily_iof(loan)

    # Assert
    # 180 days * 0.0082% = 1.476% of 10000 = 147.60
    expected = Decimal("10000.00") * Decimal("0.000082") * Decimal("180")
    assert result == expected
    assert result == Decimal("147.60")


@pytest.mark.django_db
@freeze_time("2025-01-01")
def test_calculate_daily_iof_365_days_at_limit(iof_calculator):
    """Test daily IOF calculation at annual limit
    (366 days in 2024, limit applies).
    """
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 1, 1),
    )

    # Act
    result = iof_calculator.calculate_daily_iof(loan)

    # Assert
    # 366 days (2024 is leap year) * 0.0082% = 3.0012% of 10000 = 300.12
    # But limit is 3% = 300.00, so result should be capped at 300.00
    limit = Decimal("10000.00") * Decimal("0.03")
    assert result == limit
    assert result == Decimal("300.00")


@pytest.mark.django_db
@freeze_time("2025-07-01")
def test_calculate_daily_iof_exceeds_annual_limit(iof_calculator):
    """Test daily IOF calculation when days exceed annual limit."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 1, 1),
    )

    # Act
    result = iof_calculator.calculate_daily_iof(loan)

    # Assert
    # 545 days * 0.0082% = 4.469% of 10000 = 446.90
    # But limit is 3% = 300.00, so result should be capped at 300.00
    annual_limit = Decimal("10000.00") * Decimal("0.03")
    assert result == annual_limit
    assert result == Decimal("300.00")


@pytest.mark.django_db
@freeze_time("2024-01-15")
def test_calculate_daily_iof_same_day_returns_zero(iof_calculator):
    """Test daily IOF calculation for same day returns zero."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 1, 15),
    )

    # Act
    result = iof_calculator.calculate_daily_iof(loan)

    # Assert
    assert result == Decimal("0.00")


@pytest.mark.django_db
def test_calculate_daily_iof_with_reference_date(iof_calculator):
    """Test daily IOF calculation with custom reference date."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 1, 1),
    )
    reference_date = date(2024, 2, 1)  # 31 days

    # Act
    result = iof_calculator.calculate_daily_iof(loan, reference_date)

    # Assert
    # 31 days * 0.0082% = 0.2542% of 10000 = 25.42
    expected = Decimal("10000.00") * Decimal("0.000082") * Decimal("31")
    assert result == expected
    assert result == Decimal("25.42")


@pytest.mark.django_db
def test_calculate_days_end_before_start_returns_zero(iof_calculator):
    """Test _calculate_days returns 0 when end_date is before start_date."""
    # Arrange
    start_date = date(2024, 2, 1)
    end_date = date(2024, 1, 1)

    # Act
    result = iof_calculator._calculate_days(start_date, end_date)

    # Assert
    assert result == 0


@pytest.mark.django_db
@freeze_time("2024-07-01")
def test_calculate_total_iof(iof_calculator):
    """Test total IOF calculation (fixed + daily)."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 6, 1),  # 30 days ago
    )

    # Act
    result = iof_calculator.calculate_total_iof(loan)

    # Assert
    # Fixed: 10000 * 0.0038 = 38.00
    # Daily: 10000 * 0.000082 * 30 = 24.60
    # Total: 38.00 + 24.60 = 62.60
    fixed_iof = Decimal("38.00")
    daily_iof = Decimal("24.60")
    expected = fixed_iof + daily_iof
    assert result == expected
    assert result == Decimal("62.60")


@pytest.mark.django_db
@freeze_time("2024-07-01")
def test_calculate_total_iof_with_reference_date(iof_calculator):
    """Test total IOF calculation with custom reference date."""
    # Arrange
    loan = LoanFactory(
        amount=Decimal("10000.00"),
        request_date=date(2024, 1, 1),
    )
    reference_date = date(2024, 7, 1)  # 182 days

    # Act
    result = iof_calculator.calculate_total_iof(loan, reference_date)

    # Assert
    # Fixed: 10000 * 0.0038 = 38.00
    # Daily: 10000 * 0.000082 * 182 = 149.24
    # Total: 38.00 + 149.24 = 187.24
    fixed_iof = Decimal("38.00")
    daily_iof = Decimal("10000.00") * Decimal("0.000082") * Decimal("182")
    expected = fixed_iof + daily_iof
    assert result == expected
