from datetime import date
from decimal import Decimal

from rest_framework.exceptions import ValidationError

from apps.core.services.base.base_service import BaseService
from apps.loans.models import Loan
from apps.loans.services.outstanding_balance_calculator_svc import (
    OutstandingBalanceCalculatorService,
)


class PaymentValidatorService(BaseService):
    """Service for validating payment business rules."""

    def __init__(
        self,
        outstanding_balance_calculator: OutstandingBalanceCalculatorService = None,  # noqa: E501
    ):
        """
        Initialize the service with dependencies.

        Args:
            outstanding_balance_calculator: Service for calculating
            outstanding balance
        """
        super().__init__()
        self.outstanding_balance_calculator = (
            outstanding_balance_calculator
            or OutstandingBalanceCalculatorService()
        )

    def validate_payment(
        self, payment_date, payment_value: Decimal, loan: Loan
    ) -> None:
        """
        Validate payment business rules.

        Validates:
        1. payment_date >= loan.request_date
        2. payment_value > 0
        3. payment_value <= outstanding_balance

        Args:
            payment_date: The payment date
            payment_value: The payment value
            loan: The loan instance

        Raises:
            ValidationError: If any validation rule fails
        """
        # Validate payment date
        if payment_date < loan.request_date:
            raise ValidationError(
                {
                    "payment_date": (
                        f"Payment date ({payment_date}) cannot be before "
                        f"loan request date ({loan.request_date})"
                    )
                }
            )

        # Validate payment date is not in the future
        if payment_date > date.today():
            raise ValidationError(
                {
                    "payment_date": (
                        f"Payment date ({payment_date}) cannot be in the future. "  # noqa: E501
                        f"Maximum allowed date is today ({date.today()})"
                    )
                }
            )

        # Validate payment value is positive
        if payment_value <= 0:
            raise ValidationError(
                {
                    "payment_value": (
                        f"Payment value must be greater than 0, "
                        f"got {payment_value}"
                    )
                }
            )

        # Calculate outstanding balance
        outstanding_balance = self.outstanding_balance_calculator.calculate(
            loan
        )

        # Validate payment value doesn't exceed outstanding balance
        if payment_value > outstanding_balance:
            raise ValidationError(
                {
                    "payment_value": (
                        f"Payment value ({payment_value}) cannot exceed "
                        f"outstanding balance ({outstanding_balance})"
                    )
                }
            )

        self.logger.debug(
            f"Payment validation passed for loan {loan.uuid}: "
            f"date={payment_date}, value={payment_value}, "
            f"outstanding_balance={outstanding_balance}"
        )
