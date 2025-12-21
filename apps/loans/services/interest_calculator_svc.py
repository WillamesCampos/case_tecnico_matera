from decimal import Decimal

from apps.core.services.base.base_service import BaseService


class InterestCalculatorService(BaseService):
    """Service for calculating compound interest."""

    def calculate_compound_interest(
        self, loan_amount: Decimal, rate_percent: Decimal, months: int
    ) -> Decimal:
        """
        Calculate compound interest.

        Args:
            principal: The principal amount (loan amount)
            rate_percent: Interest rate in percentage (e.g., 2.5 for 2.5%)
            months: Number of months

        Returns:
            The principal amount with compound interest applied
        """
        if months < 0:
            return loan_amount

        rate_decimal = rate_percent / Decimal("100")
        multiplier = (Decimal("1") + rate_decimal) ** months
        result = loan_amount * multiplier

        self.logger.debug(
            f"Compound interest calculated: loan_amount={loan_amount}, "
            f"rate={rate_percent}%, months={months}, result={result}"
        )
        return result
