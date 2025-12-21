from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from apps.core.services.base.base_service import BaseService
from apps.loans.models import Loan
from apps.loans.services.interest_calculator_svc import (
    InterestCalculatorService,
)
from apps.loans.services.iof_calculator_svc import IOFCalculatorService
from apps.loans.services.payment_aggregator_svc import PaymentAggregatorService


class OutstandingBalanceCalculatorService(BaseService):
    """Service for calculating outstanding balance (saldo devedor)."""

    def __init__(
        self,
        interest_calculator: InterestCalculatorService = None,
        payment_aggregator: PaymentAggregatorService = None,
        iof_calculator: IOFCalculatorService = None,
    ):
        """
        Initialize the service with dependencies.

        Args:
            interest_calculator: Service for calculating interest (injected)
            payment_aggregator: Service for aggregating payments (injected)
            iof_calculator: Service for calculating IOF (injected)
        """
        super().__init__()
        self.interest_calculator = (
            interest_calculator or InterestCalculatorService()
        )
        self.payment_aggregator = (
            payment_aggregator or PaymentAggregatorService()
        )
        self.iof_calculator = iof_calculator or IOFCalculatorService()

    def calculate(self, loan: Loan, reference_date: date = None) -> Decimal:
        """
        Calculate the outstanding balance for a loan.

        Formula: (Principal + Interest + IOF) - Total Paid
        If result is negative, returns 0 (no negative balance allowed).

        Args:
            loan: The loan instance
            reference_date: Date to calculate balance as of (defaults to today)

        Returns:
            The outstanding balance (Decimal, minimum 0)
        """
        if reference_date is None:
            reference_date = date.today()

        # Calculate months between request_date and reference_date
        months = self._calculate_months(loan.request_date, reference_date)

        # Calculate amount with compound interest
        amount_with_interest = (
            self.interest_calculator.calculate_compound_interest(
                loan_amount=loan.amount,
                rate_percent=loan.interest_rate,
                months=months,
            )
        )

        # Calculate IOF (fixed + daily)
        total_iof = self.iof_calculator.calculate_total_iof(
            loan, reference_date
        )

        # Get total paid
        total_paid = self.payment_aggregator.get_total_paid(loan)

        # Calculate outstanding balance:
        # (Principal + Interest + IOF) - Total Paid
        outstanding_balance = amount_with_interest + total_iof - total_paid
        result = max(Decimal("0.00"), outstanding_balance)

        self.logger.debug(
            f"Outstanding balance calculated for loan {loan.uuid}: "
            f"amount={loan.amount}, months={months}, "
            f"amount_with_interest={amount_with_interest}, "
            f"total_iof={total_iof}, total_paid={total_paid}, result={result}"
        )
        return result

    def _calculate_months(self, start_date: date, end_date: date) -> int:
        """
        Calculate the number of complete months between two dates.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Number of complete months (0 if end_date is before start_date)
        """
        if end_date < start_date:
            return 0

        delta = relativedelta(end_date, start_date)
        return delta.years * 12 + delta.months
