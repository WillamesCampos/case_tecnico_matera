from django.contrib import admin

from apps.loans.models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = [
        "uuid",
        "owner",
        "bank",
        "amount",
        "interest_rate",
        "request_date",
        "request_ip",
        "created_at",
    ]
    list_filter = [
        "request_date",
        "created_at",
        "bank",
        "interest_rate",
    ]
    search_fields = [
        "uuid",
        "owner__username",
        "owner__email",
        "bank",
    ]
    readonly_fields = [
        "uuid",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "request_ip",
    ]
    fieldsets = (
        (
            "Informações Básicas",
            {
                "fields": (
                    "uuid",
                    "owner",
                    "bank",
                )
            },
        ),
        (
            "Valores",
            {
                "fields": (
                    "amount",
                    "interest_rate",
                )
            },
        ),
        (
            "Datas e IP",
            {
                "fields": (
                    "request_date",
                    "request_ip",
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
    raw_id_fields = ["owner"]
    date_hierarchy = "request_date"
    ordering = ["-request_date", "-created_at"]
