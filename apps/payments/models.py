from django.db import models

from apps.core.models import BaseModel
from apps.loans.models import Loan


class Payment(BaseModel):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Loan",
        help_text="The loan that the payment is for",
        db_index=True,
    )
    payment_date = models.DateField(
        verbose_name="Payment Date",
        help_text="The date the payment was made",
        db_index=True,
    )
    payment_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Payment Value",
        help_text="The value of the payment",
        db_index=True,
    )

    class Meta:
        ordering = ["-payment_date", "-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

        indexes = [
            models.Index(
                fields=["loan", "-payment_date"], name="payment_loan_date_idx"
            ),
            models.Index(
                fields=["loan", "-created_at"], name="payment_loan_created_idx"
            ),
        ]

        # data integrity
        constraints = [
            models.CheckConstraint(
                condition=models.Q(payment_value__gt=0),
                name="payment_value_positive",
            )
        ]

    def __str__(self):
        return f"Payment {self.uuid} - R$ {self.payment_value}"
