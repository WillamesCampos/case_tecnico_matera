from rest_framework import serializers


class AuditSerializerMixin(serializers.Serializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    updated_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
