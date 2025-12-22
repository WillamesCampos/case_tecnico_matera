from django.contrib import admin

from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "loan",
        "payment_value",
        "payment_date",
        "created_at",
    ]
    list_filter = [
        "payment_date",
        "created_at",
    ]
    search_fields = [
        "uuid",
        "loan__uuid",
        "loan__owner__username",
        "loan__owner__email",
    ]
    readonly_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    ]
    fieldsets = (
        (
            "Informações Básicas",
            {
                "fields": (
                    "uuid",
                    "loan",
                )
            },
        ),
        (
            "Pagamento",
            {
                "fields": (
                    "payment_value",
                    "payment_date",
                )
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    raw_id_fields = ["loan"]
    date_hierarchy = "payment_date"
    ordering = ["-payment_date", "-created_at"]
