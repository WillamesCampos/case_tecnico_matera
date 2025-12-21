from datetime import date
from decimal import Decimal

from apps.core.services.base.base_service import BaseService
from apps.loans.models import Loan


class IOFCalculatorService(BaseService):
    """Service for calculating IOF (Imposto sobre Operações Financeiras)."""

    # IOF rates for pessoa física (individual)
    FIXED_RATE = Decimal("0.0038")  # 0.38%
    DAILY_RATE = Decimal("0.000082")  # 0.0082% per day
    ANNUAL_LIMIT = Decimal("0.03")  # 3% per year (365 days)

    def calculate_fixed_iof(self, loan_amount: Decimal) -> Decimal:
        """
        Calculate fixed IOF (0.38% of loan amount).

        Args:
            loan_amount: The original loan amount

        Returns:
            The fixed IOF amount
        """
        fixed_iof = loan_amount * self.FIXED_RATE

        self.logger.debug(
            f"Fixed IOF calculated: loan_amount={loan_amount}, "
            f"rate={self.FIXED_RATE}, result={fixed_iof}"
        )
        return fixed_iof

    def calculate_daily_iof(
        self, loan: Loan, reference_date: date = None
    ) -> Decimal:
        """
        Calculate daily IOF (Imposto sobre Operações Financeiras).
        (0.0082% per day on original amount, capped at 3% per year).

        Args:
            loan: The loan instance
            reference_date: Date to calculate IOF as of (defaults to today)

        Returns:
            The daily IOF amount (capped at 3% of loan amount per year)
        """
        if reference_date is None:
            reference_date = date.today()

        # Calculate days between request_date and reference_date
        days = self._calculate_days(loan.request_date, reference_date)

        # Calculate daily IOF: 0.0082% per day on original amount
        daily_iof_unlimited = loan.amount * self.DAILY_RATE * Decimal(days)

        # Apply annual limit: maximum 3% of loan amount per year
        annual_limit = loan.amount * self.ANNUAL_LIMIT
        daily_iof = min(daily_iof_unlimited, annual_limit)

        self.logger.debug(
            f"Daily IOF calculated for loan {loan.uuid}: "
            f"amount={loan.amount}, days={days}, "
            f"unlimited={daily_iof_unlimited}, limit={annual_limit}, "
            f"result={daily_iof}"
        )
        return daily_iof

    def calculate_total_iof(
        self, loan: Loan, reference_date: date = None
    ) -> Decimal:
        """
        Calculate total IOF (fixed + daily).

        Args:
            loan: The loan instance
            reference_date: Date to calculate IOF as of (defaults to today)

        Returns:
            The total IOF amount
        """
        fixed_iof = self.calculate_fixed_iof(loan.amount)
        daily_iof = self.calculate_daily_iof(loan, reference_date)
        total_iof = fixed_iof + daily_iof

        self.logger.debug(
            f"Total IOF calculated for loan {loan.uuid}: "
            f"fixed={fixed_iof}, daily={daily_iof}, total={total_iof}"
        )
        return total_iof

    def _calculate_days(self, start_date: date, end_date: date) -> int:
        """
        Calculate the number of days between two dates.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Number of days (0 if end_date is before start_date)
        """
        if end_date < start_date:
            return 0

        delta = end_date - start_date
        return delta.days
