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

    # TODO: Add validation for payment date to be after loan request date
    # TODO: Add validation for payment value to be greater than 0
    # TODO: Add validation for payment value to be less than the loan amount
    # remaining


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
