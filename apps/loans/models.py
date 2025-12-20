from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

from apps.core.models import BaseModel

User = get_user_model()


class Loan(BaseModel):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="loans",
        db_index=True,
        verbose_name="Owner",
        help_text="The user who owns the loan",
    )
    bank = models.CharField(
        max_length=255,
        verbose_name="Bank",
        help_text="The bank that lent the money",
        db_index=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount",
        help_text="The amount of money borrowed",
    )
    interest_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Interest Rate",
        help_text="Monthly interest rate in percentage (e.g., 2.5 for 2.5%)",
    )

    request_date = models.DateField(
        db_index=True,
        verbose_name="Request Date",
        help_text="The date the loan was requested",
    )
    request_ip = models.GenericIPAddressField()

    class Meta:
        ordering = ["-request_date", "-created_at"]
        verbose_name = "Loan"
        verbose_name_plural = "Loans"

        indexes = [
            models.Index(
                fields=["owner", "-request_date"], name="loan_owner_date_idx"
            ),
            models.Index(
                fields=["owner", "-created_at"], name="loan_owner_created_idx"
            ),
        ]

        # data integrity
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0), name="loan_amount_positive"
            ),
            models.CheckConstraint(
                condition=Q(interest_rate__gte=0) & Q(interest_rate__lte=100),
                name="loan_interest_rate_range",
            ),
        ]

    def __str__(self):
        return f"Loan {self.uuid} - {self.interest_rate} - R$ {self.amount}"
