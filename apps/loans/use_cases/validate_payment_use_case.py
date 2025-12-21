from datetime import date
from decimal import Decimal

from apps.core.use_cases.base.base_use_case import BaseUseCase
from apps.loans.models import Loan
from apps.loans.services.payment_validator_svc import PaymentValidatorService


class ValidatePaymentUseCase(BaseUseCase):
    """Use case for validating payment business rules."""

    def __init__(self, payment_validator: PaymentValidatorService = None):
        """
        Initialize the use case with dependencies.

        Args:
            payment_validator: Service for validating payments
        """
        super().__init__()
        self.payment_validator = payment_validator or PaymentValidatorService()

    def execute(
        self, payment_date: date, payment_value: Decimal, loan: Loan
    ) -> None:
        """
        Execute the use case to validate payment.

        Args:
            payment_date: The payment date
            payment_value: The payment value
            loan: The loan instance

        Raises:
            ValidationError: If validation fails
        """
        self.logger.debug(
            f"Validating payment for loan {loan.uuid}: "
            f"date={payment_date}, value={payment_value}"
        )

        self.payment_validator.validate_payment(
            payment_date, payment_value, loan
        )

        self.logger.info(
            f"Payment validation passed for loan {loan.uuid}: "
            f"date={payment_date}, value={payment_value}"
        )
