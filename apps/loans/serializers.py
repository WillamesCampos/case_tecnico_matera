from decimal import Decimal

from rest_framework import serializers

from apps.core.serializers.mixins.audit_serializer_mixin import (
    AuditSerializerMixin,
)
from apps.core.serializers.user_serializer import UserSerializer
from apps.loans.models import Loan
from apps.loans.services.iof_calculator_svc import IOFCalculatorService
from apps.loans.services.payment_aggregator_svc import PaymentAggregatorService
from apps.loans.use_cases.calculate_loan_outstanding_balance_use_case import (
    CalculateLoanOutstandingBalanceUseCase,
)


class LoanSerializer(serializers.ModelSerializer, AuditSerializerMixin):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    total_paid = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()
    iof = serializers.SerializerMethodField()

    critical_fields = ["owner", "bank", "amount", "interest_rate"]

    def _disable_critical_fields(self):
        """Disable critical fields for update operations."""
        for field in self.critical_fields:
            self.fields[field].read_only = True

    def _manage_critical_fields(self):
        """Manage critical fields for update operations."""
        if self.instance:
            has_payments = self.instance.payments.exists()
            if has_payments:
                self._disable_critical_fields()

    def __init__(self, *args, **kwargs):
        """Initialize services for calculating totals."""
        super().__init__(*args, **kwargs)
        self.payment_aggregator = PaymentAggregatorService()
        self.outstanding_balance_use_case = (
            CalculateLoanOutstandingBalanceUseCase()
        )
        self.iof_calculator = IOFCalculatorService()

        self._manage_critical_fields()

    def get_total_paid(self, obj):
        """Calculate total paid amount for the loan."""
        return float(self.payment_aggregator.get_total_paid(obj))

    def get_remaining_balance(self, obj):
        """Calculate outstanding balance (saldo devedor) for the loan."""
        balance = self.outstanding_balance_use_case.execute(obj)
        return float(balance)

    def get_iof(self, obj):
        """Calculate total IOF (fixed + daily) for the loan."""
        total_iof = self.iof_calculator.calculate_total_iof(obj)
        return float(total_iof)

    def get_request_ip(self):
        """Get the request IP from the context."""
        request = self.context["request"]

        # Check X-Forwarded-For (for proxies/load balancers)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR") or "0.0.0.0"

    class Meta:
        model = Loan
        fields = "__all__"
        read_only_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "request_ip",
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

    def validate_interest_rate(self, value):
        if value < Decimal("0.1"):
            raise serializers.ValidationError(
                "Interest rate must be greater than or equal to 0.1"
            )
        return value

    def create(self, validated_data):
        validated_data["request_ip"] = self.get_request_ip()
        return super().create(validated_data)


class LoanListSerializer(serializers.ModelSerializer):
    """Simplified serializer for loan list view (no expensive calculations)."""

    owner = UserSerializer()

    class Meta:
        model = Loan
        fields = [
            "uuid",
            "owner",
            "bank",
            "amount",
            "interest_rate",
            "request_date",
            "created_at",
        ]
        read_only_fields = fields
