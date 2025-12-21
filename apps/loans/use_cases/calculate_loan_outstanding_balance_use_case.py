from datetime import date
from decimal import Decimal

from apps.core.use_cases.base.base_use_case import BaseUseCase
from apps.loans.models import Loan
from apps.loans.services.outstanding_balance_calculator_svc import (
    OutstandingBalanceCalculatorService,
)


class CalculateLoanOutstandingBalanceUseCase(BaseUseCase):
    """Use case for calculating loan outstanding balance."""

    def __init__(
        self,
        outstanding_balance_calculator: OutstandingBalanceCalculatorService = None,  # noqa: E501
    ):
        """
        Initialize the use case with dependencies.

        Args:
            outstanding_balance_calculator: Service for calculating
            outstanding balance
        """
        super().__init__()
        self.outstanding_balance_calculator = (
            outstanding_balance_calculator
            or OutstandingBalanceCalculatorService()
        )

    def execute(self, loan: Loan, reference_date: date = None) -> Decimal:
        """
        Execute the use case to calculate outstanding balance.

        Args:
            loan: The loan instance
            reference_date: Date to calculate balance as of (defaults to today)

        Returns:
            The outstanding balance (Decimal)
        """
        self.logger.debug(
            f"Calculating outstanding balance for loan {loan.uuid}, "
            f"reference_date={reference_date}"
        )

        result = self.outstanding_balance_calculator.calculate(
            loan, reference_date
        )

        self.logger.info(
            f"Outstanding balance calculated for loan {loan.uuid}: {result}"
        )
        return result
