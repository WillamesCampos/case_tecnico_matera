from rest_framework import serializers

from apps.core.serializers.mixins.audit_serializer_mixin import (
    AuditSerializerMixin,
)
from apps.core.serializers.user_serializer import UserSerializer
from apps.loans.models import Loan


class LoanSerializer(serializers.ModelSerializer, AuditSerializerMixin):
    owner = UserSerializer()
    total_paid = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()
    # TODO: total_paid field must be calculated based on the payments
    # TODO: remaining_balance field must be calculated based on the payments

    def get_total_paid(self, obj):
        return 0.0

    def get_remaining_balance(self, obj):
        return float(obj.amount) - self.get_total_paid(obj)

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
        if value <= 0:
            raise serializers.ValidationError(
                "Interest rate must be greater than 0"
            )
        return value

    def create(self, validated_data):
        validated_data["request_ip"] = self.context["request"].META.get(
            "REMOTE_ADDR"
        )
        return super().create(validated_data)
