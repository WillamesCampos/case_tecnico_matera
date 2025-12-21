from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from rest_framework import serializers

from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.loans.serializers import LoanListSerializer, LoanSerializer


@pytest.mark.django_db
def test_loan_serializer_returns_all_fields():
    """Test that LoanSerializer returns all expected fields."""
    # Arrange
    loan = LoanFactory()
    serializer = LoanSerializer(loan)

    # Act
    data = serializer.data

    # Assert
    assert "uuid" in data
    assert "bank" in data
    assert "amount" in data
    assert "interest_rate" in data
    assert "request_date" in data
    assert "request_ip" in data
    assert "total_paid" in data
    assert "remaining_balance" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.django_db
@patch("apps.loans.serializers.PaymentAggregatorService")
def test_loan_serializer_get_total_paid_calls_service(mock_service_class):
    """Test that get_total_paid calls PaymentAggregatorService."""
    # Arrange
    loan = LoanFactory()
    mock_service = MagicMock()
    mock_service.get_total_paid.return_value = Decimal("1000.00")
    mock_service_class.return_value = mock_service

    serializer = LoanSerializer(loan)
    serializer.payment_aggregator = mock_service

    # Act
    total_paid = serializer.get_total_paid(loan)

    # Assert
    mock_service.get_total_paid.assert_called_once_with(loan)
    assert total_paid == 1000.0


@pytest.mark.django_db
@patch("apps.loans.serializers.CalculateLoanOutstandingBalanceUseCase")
def test_loan_serializer_get_remaining_balance_calls_use_case(
    mock_use_case_class,
):
    """Test that get_remaining_balance calls
    CalculateLoanOutstandingBalanceUseCase.
    """
    # Arrange
    loan = LoanFactory()
    mock_use_case = MagicMock()
    mock_use_case.execute.return_value = Decimal("5000.00")
    mock_use_case_class.return_value = mock_use_case

    serializer = LoanSerializer(loan)
    serializer.outstanding_balance_use_case = mock_use_case

    # Act
    remaining_balance = serializer.get_remaining_balance(loan)

    # Assert
    mock_use_case.execute.assert_called_once_with(loan)
    assert remaining_balance == 5000.0


@pytest.mark.django_db
def test_loan_serializer_validate_amount_positive():
    """Test that validate_amount accepts positive values."""
    # Arrange
    serializer = LoanSerializer()

    # Act
    result = serializer.validate_amount(Decimal("1000.00"))

    # Assert
    assert result == Decimal("1000.00")


@pytest.mark.django_db
def test_loan_serializer_validate_amount_zero_raises_error():
    """Test that validate_amount raises error for zero."""
    # Arrange
    serializer = LoanSerializer()

    # Act & Assert
    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate_amount(Decimal("0.00"))

    assert "greater than 0" in str(exc_info.value)


@pytest.mark.django_db
def test_loan_serializer_validate_amount_negative_raises_error():
    """Test that validate_amount raises error for negative values."""
    # Arrange
    serializer = LoanSerializer()

    # Act & Assert
    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate_amount(Decimal("-100.00"))

    assert "greater than 0" in str(exc_info.value)


@pytest.mark.django_db
def test_loan_serializer_validate_interest_rate_minimum():
    """Test that validate_interest_rate accepts values >= 0.1."""
    # Arrange
    serializer = LoanSerializer()

    # Act
    result = serializer.validate_interest_rate(Decimal("0.1"))

    # Assert
    assert result == Decimal("0.1")


@pytest.mark.django_db
def test_loan_serializer_validate_interest_rate_below_minimum_raises_error():
    """Test that validate_interest_rate raises error for values < 0.1."""
    # Arrange
    serializer = LoanSerializer()

    # Act & Assert
    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate_interest_rate(Decimal("0.05"))

    assert "greater than or equal to 0.1" in str(exc_info.value)


@pytest.mark.django_db
def test_loan_serializer_validate_interest_rate_zero_raises_error():
    """Test that validate_interest_rate raises error for zero."""
    # Arrange
    serializer = LoanSerializer()

    # Act & Assert
    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate_interest_rate(Decimal("0.00"))

    assert "greater than or equal to 0.1" in str(exc_info.value)


@pytest.mark.django_db
def test_loan_serializer_get_request_ip_from_remote_addr():
    """Test that get_request_ip extracts IP from REMOTE_ADDR."""
    # Arrange
    loan = LoanFactory()
    mock_request = MagicMock()
    mock_request.META = {"REMOTE_ADDR": "192.168.1.1"}

    serializer = LoanSerializer(loan, context={"request": mock_request})

    # Act
    ip = serializer.get_request_ip()

    # Assert
    assert ip == "192.168.1.1"


@pytest.mark.django_db
def test_loan_serializer_get_request_ip_from_x_forwarded_for():
    """Test that get_request_ip extracts IP from X-Forwarded-For."""
    # Arrange
    loan = LoanFactory()
    mock_request = MagicMock()
    mock_request.META = {"HTTP_X_FORWARDED_FOR": "10.0.0.1, 192.168.1.1"}

    serializer = LoanSerializer(loan, context={"request": mock_request})

    # Act
    ip = serializer.get_request_ip()

    # Assert
    assert ip == "10.0.0.1"


@pytest.mark.django_db
def test_loan_serializer_get_request_ip_fallback_to_default():
    """Test that get_request_ip returns default when no IP found."""
    # Arrange
    loan = LoanFactory()
    mock_request = MagicMock()
    mock_request.META = {}

    serializer = LoanSerializer(loan, context={"request": mock_request})

    # Act
    ip = serializer.get_request_ip()

    # Assert
    assert ip == "0.0.0.0"


@pytest.mark.django_db
def test_loan_serializer_critical_fields_read_only_when_has_payments():
    """Test that critical fields become read_only when loan has payments."""
    # Arrange
    loan = LoanFactory()
    PaymentFactory(loan=loan)

    serializer = LoanSerializer(loan)

    # Assert
    assert serializer.fields["amount"].read_only is True
    assert serializer.fields["interest_rate"].read_only is True
    assert serializer.fields["bank"].read_only is True
    assert serializer.fields["owner"].read_only is True


@pytest.mark.django_db
def test_loan_serializer_critical_fields_not_read_only_when_no_payments():
    """Test that critical fields are not read_only when
    loan has no payments
    """
    # Arrange
    loan = LoanFactory()

    serializer = LoanSerializer(loan)

    # Assert
    assert serializer.fields["amount"].read_only is False
    assert serializer.fields["interest_rate"].read_only is False
    assert serializer.fields["bank"].read_only is False
    assert serializer.fields["owner"].read_only is False


@pytest.mark.django_db
def test_loan_list_serializer_returns_limited_fields():
    """Test that LoanListSerializer returns only expected fields."""
    # Arrange
    loan = LoanFactory()
    serializer = LoanListSerializer(loan)

    # Act
    data = serializer.data

    # Assert
    assert "uuid" in data
    assert "owner" in data
    assert "bank" in data
    assert "amount" in data
    assert "interest_rate" in data
    assert "request_date" in data
    assert "created_at" in data
    assert "total_paid" not in data
    assert "remaining_balance" not in data
