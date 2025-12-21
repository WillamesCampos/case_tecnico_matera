from decimal import Decimal

from django.db.models import Sum

from apps.core.services.base.base_service import BaseService
from apps.loans.models import Loan


class PaymentAggregatorService(BaseService):
    """Service for aggregating payment amounts."""

    def get_total_paid(self, loan: Loan) -> Decimal:
        """
        Get the total amount paid for a loan.

        Uses a single aggregate query to avoid N+1 problems.

        Args:
            loan: The loan instance

        Returns:
            The total amount paid (Decimal, defaults to 0.00 if no payments)
        """
        result = loan.payments.aggregate(total=Sum("payment_value"))["total"]
        total_paid = Decimal(result) if result else Decimal("0.00")

        self.logger.debug(
            f"Total paid calculated for loan {loan.uuid}: {total_paid}"
        )
        return total_paid
