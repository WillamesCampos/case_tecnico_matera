from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from rest_framework import serializers

from apps.core.tests.factories.loan import LoanFactory
from apps.core.tests.factories.payment import PaymentFactory
from apps.core.tests.factories.user import UserFactory
from apps.payments.serializers import PaymentListSerializer, PaymentSerializer


@pytest.mark.django_db
def test_payment_serializer_returns_all_fields():
    """Test that PaymentSerializer returns all expected fields."""
    # Arrange
    payment = PaymentFactory()
    serializer = PaymentSerializer(payment)

    # Act
    data = serializer.data

    # Assert
    assert "uuid" in data
    assert "loan" in data
    assert "payment_date" in data
    assert "payment_value" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.django_db
@patch("apps.payments.serializers.ValidatePaymentUseCase")
def test_payment_serializer_validate_calls_use_case_when_all_fields_present(
    mock_use_case_class,
):
    """
    Test that validate calls ValidatePaymentUseCase when all
    fields are present.
    """
    # Arrange
    loan = LoanFactory()
    user = loan.owner
    mock_use_case = MagicMock()
    mock_use_case_class.return_value = mock_use_case

    mock_request = MagicMock()
    mock_request.user = user

    serializer = PaymentSerializer(context={"request": mock_request})
    serializer.validate_payment_use_case = mock_use_case

    attrs = {
        "loan": loan,
        "payment_date": loan.request_date,
        "payment_value": Decimal("1000.00"),
    }

    # Act
    result = serializer.validate(attrs)

    # Assert
    mock_use_case.execute.assert_called_once_with(
        payment_date=loan.request_date,
        payment_value=Decimal("1000.00"),
        loan=loan,
    )
    assert result == attrs


@pytest.mark.django_db
@patch("apps.payments.serializers.ValidatePaymentUseCase")
def test_payment_serializer_validate_does_not_call_use_case_when_fields_missing(  # noqa: E501
    mock_use_case_class,
):
    """Test that validate does not call use case when fields are missing."""
    # Arrange
    loan = LoanFactory()
    user = loan.owner
    mock_use_case = MagicMock()
    mock_use_case_class.return_value = mock_use_case

    mock_request = MagicMock()
    mock_request.user = user

    serializer = PaymentSerializer(context={"request": mock_request})
    serializer.validate_payment_use_case = mock_use_case

    attrs = {"loan": loan}

    # Act
    result = serializer.validate(attrs)

    # Assert
    mock_use_case.execute.assert_not_called()
    assert result == attrs


@pytest.mark.django_db
def test_payment_serializer_validate_ownership_success():
    """Test that validate accepts payment for user's own loan."""
    # Arrange
    loan = LoanFactory()
    user = loan.owner

    mock_request = MagicMock()
    mock_request.user = user

    serializer = PaymentSerializer(context={"request": mock_request})
    serializer.validate_payment_use_case = MagicMock()

    attrs = {
        "loan": loan,
        "payment_date": loan.request_date,
        "payment_value": Decimal("1000.00"),
    }

    # Act
    result = serializer.validate(attrs)

    # Assert
    assert result == attrs


@pytest.mark.django_db
def test_payment_serializer_validate_ownership_fails_for_other_user_loan():
    """Test that validate raises error for other user's loan."""
    # Arrange
    loan = LoanFactory()
    other_user = UserFactory()

    mock_request = MagicMock()
    mock_request.user = other_user

    serializer = PaymentSerializer(context={"request": mock_request})
    serializer.validate_payment_use_case = MagicMock()

    attrs = {
        "loan": loan,
        "payment_date": loan.request_date,
        "payment_value": Decimal("1000.00"),
    }

    # Act & Assert
    with pytest.raises(serializers.ValidationError) as exc_info:
        serializer.validate(attrs)

    assert "own loans" in str(exc_info.value)


@pytest.mark.django_db
def test_payment_list_serializer_returns_limited_fields():
    """Test that PaymentListSerializer returns only expected fields."""
    # Arrange
    payment = PaymentFactory()
    serializer = PaymentListSerializer(payment)

    # Act
    data = serializer.data

    # Assert
    assert "uuid" in data
    assert "payment_date" in data
    assert "payment_value" in data
    assert "loan" not in data
    assert "created_at" not in data
