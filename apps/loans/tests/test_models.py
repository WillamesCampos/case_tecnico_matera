from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.user import UserFactory
from apps.loans.models import Loan


@pytest.mark.django_db
def test_loan_amount_cannot_be_zero():
    """Test that loan amount cannot be 0."""
    # Arrange
    owner = UserFactory()

    # Act & Assert
    with pytest.raises(IntegrityError):
        Loan.objects.create(
            owner=owner,
            bank="Test Bank",
            amount=Decimal("0.00"),
            interest_rate=Decimal("2.5"),
            request_ip="127.0.0.1",
        )


@pytest.mark.django_db
def test_loan_amount_cannot_be_negative():
    """Test that loan amount cannot be negative."""
    # Arrange
    owner = UserFactory()

    # Act & Assert
    with pytest.raises(IntegrityError):
        Loan.objects.create(
            owner=owner,
            bank="Test Bank",
            amount=Decimal("-100.00"),
            interest_rate=Decimal("2.5"),
            request_ip="127.0.0.1",
        )


@pytest.mark.django_db
def test_loan_amount_can_be_positive():
    """Test that loan amount can be positive."""
    # Arrange
    owner = UserFactory()

    # Act
    loan = LoanFactory(owner=owner, amount=Decimal("1000.00"))

    # Assert
    assert loan.amount > 0


@pytest.mark.django_db
def test_loan_interest_rate_cannot_be_negative():
    """Test that interest rate cannot be negative."""
    # Arrange
    owner = UserFactory()

    # Act & Assert
    with pytest.raises(IntegrityError):
        Loan.objects.create(
            owner=owner,
            bank="Test Bank",
            amount=Decimal("1000.00"),
            interest_rate=Decimal("-1.00"),
            request_ip="127.0.0.1",
        )


@pytest.mark.django_db
def test_loan_interest_rate_cannot_exceed_100():
    """Test that interest rate cannot exceed 100."""
    # Arrange
    owner = UserFactory()

    # Act & Assert
    with pytest.raises(IntegrityError):
        Loan.objects.create(
            owner=owner,
            bank="Test Bank",
            amount=Decimal("1000.00"),
            interest_rate=Decimal("101.00"),
            request_ip="127.0.0.1",
        )


@pytest.mark.django_db
def test_loan_interest_rate_can_be_zero():
    """Test that interest rate can be 0."""
    # Arrange
    owner = UserFactory()

    # Act
    loan = LoanFactory(owner=owner, interest_rate=Decimal("0.00"))

    # Assert
    assert loan.interest_rate == Decimal("0.00")


@pytest.mark.django_db
def test_loan_interest_rate_can_be_100():
    """Test that interest rate can be 100."""
    # Arrange
    owner = UserFactory()

    # Act
    loan = LoanFactory(owner=owner, interest_rate=Decimal("100.00"))

    # Assert
    assert loan.interest_rate == Decimal("100.00")


@pytest.mark.django_db
def test_loan_interest_rate_can_be_within_range():
    """Test that interest rate can be between 0 and 100."""
    # Arrange
    owner = UserFactory()

    # Act
    loan = LoanFactory(owner=owner, interest_rate=Decimal("2.5"))

    # Assert
    assert Decimal("0") <= loan.interest_rate <= Decimal("100")
