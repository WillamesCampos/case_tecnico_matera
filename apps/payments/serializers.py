from rest_framework import serializers

from apps.core.serializers.mixins.audit_serializer_mixin import (
    AuditSerializerMixin,
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

    def validate_payment_date(self, value):
        if value < self.instance.loan.request_date:
            raise serializers.ValidationError(
                "Payment date must be after loan request date"
            )
        return value


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
