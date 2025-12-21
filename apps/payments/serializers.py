from rest_framework import serializers

from apps.core.serializers.mixins.audit_serializer_mixin import (
    AuditSerializerMixin,
)
from apps.loans.use_cases.validate_payment_use_case import (
    ValidatePaymentUseCase,
)
from apps.payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer, AuditSerializerMixin):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "uuid",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize use case for payment validation."""
        super().__init__(*args, **kwargs)
        self.validate_payment_use_case = ValidatePaymentUseCase()

    def validate_payment_value(self, value):
        """Validate payment value is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Payment value must be greater than 0"
            )
        return value

    def validate(self, attrs):
        super().validate(attrs)

        # For update, get values from
        # attrs (new values) or instance (existing values)
        loan = attrs.get("loan")
        if not loan and self.instance:
            loan = self.instance.loan

        payment_date = attrs.get("payment_date")
        if not payment_date and self.instance:
            payment_date = self.instance.payment_date

        payment_value = attrs.get("payment_value")
        if payment_value is None and self.instance:
            payment_value = self.instance.payment_value

        if loan:
            user = self.context["request"].user
            if loan.owner != user:
                raise serializers.ValidationError(
                    {
                        "loan": "You can only create/update payments for your own loans"  # noqa: E501
                    }
                )

        if all([loan, payment_date, payment_value]):
            self.validate_payment_use_case.execute(
                payment_date=payment_date,
                payment_value=payment_value,
                loan=loan,
            )

        return attrs


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for displaying payments in loan detail.
    """

    class Meta:
        model = Payment
        fields = [
            "uuid",
            "payment_date",
            "payment_value",
        ]
        read_only_fields = fields
