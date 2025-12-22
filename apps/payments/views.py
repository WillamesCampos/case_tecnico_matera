from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.payments.filters import PaymentFilter
from apps.payments.models import Payment
from apps.payments.serializers import PaymentSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Payments"],
        summary="Listar pagamentos",
        description=(
            "Retorna uma lista paginada de pagamentos dos empréstimos "
            "do usuário autenticado. Suporta filtros por empréstimo, "
            "data e valor. Exemplos de filtros: "
            "`?loan=<uuid>&payment_date__gte=2024-01-01&payment_value__gte=100`"
        ),
    ),
    create=extend_schema(
        tags=["Payments"],
        summary="Criar pagamento",
        description="""
        Registra um novo pagamento para um empréstimo.

        **Campos obrigatórios:**
        - `loan`: UUID do empréstimo (deve pertencer ao usuário
          autenticado)
        - `payment_date`: Data do pagamento (deve ser >= data de
          solicitação do empréstimo e não pode ser futura)
        - `payment_value`: Valor do pagamento (deve ser > 0 e <=
          saldo devedor atual)

        **Validações:**
        - O empréstimo deve pertencer ao usuário autenticado
        - A data do pagamento não pode ser anterior à data de
          solicitação do empréstimo
        - A data do pagamento não pode ser futura
        - O valor do pagamento não pode exceder o saldo devedor atual
        """,
    ),
    retrieve=extend_schema(
        tags=["Payments"],
        summary="Detalhar pagamento",
        description="Retorna os detalhes completos de um pagamento.",
    ),
    update=extend_schema(
        tags=["Payments"],
        summary="Atualizar pagamento completo",
        description="""
        Atualiza todos os campos de um pagamento.

        **Validações:**
        - Todas as validações de criação se aplicam
        - O empréstimo associado deve pertencer ao usuário autenticado
        """,
    ),
    partial_update=extend_schema(
        tags=["Payments"],
        summary="Atualizar pagamento parcialmente",
        description="""
        Atualiza campos específicos de um pagamento.

        **Validações:**
        - Todas as validações de criação se aplicam
        - O empréstimo associado deve pertencer ao usuário autenticado
        """,
    ),
    destroy=extend_schema(
        tags=["Payments"],
        summary="Excluir pagamento",
        description=(
            "Exclui um pagamento. Apenas pagamentos de empréstimos "
            "próprios podem ser excluídos."
        ),
    ),
)
class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    search_fields = ["uuid", "loan__uuid"]
    ordering_fields = [
        "payment_date",
        "payment_value",
        "created_at",
    ]
    ordering = ["-payment_date"]

    def get_queryset(self):
        return Payment.objects.filter(loan__owner=self.request.user)
