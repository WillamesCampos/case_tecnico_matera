from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets

from apps.loans.models import Loan
from apps.loans.serializers import LoanListSerializer, LoanSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Loans"],
        summary="Listar empréstimos",
        description=(
            "Retorna uma lista paginada de empréstimos do usuário autenticado."
        ),
    ),
    create=extend_schema(
        tags=["Loans"],
        summary="Criar empréstimo",
        description="""
        Cria um novo empréstimo para o usuário autenticado.

        **Campos obrigatórios:**
        - `amount`: Valor nominal do empréstimo (deve ser > 0)
        - `interest_rate`: Taxa de juros mensal (deve ser >= 0.1%)
        - `bank`: Informações do banco (texto)
        - `customer`: Informações do cliente (texto)

        **Campos automáticos:**
        - `uuid`: Identificador único gerado automaticamente
        - `request_date`: Data de solicitação (padrão: data atual)
        - `request_ip`: IP de origem capturado automaticamente
        """,
    ),
    retrieve=extend_schema(
        tags=["Loans"],
        summary="Detalhar empréstimo",
        description="""
        Retorna os detalhes completos de um empréstimo, incluindo:
        - Informações básicas do empréstimo
        - Total pago até o momento
        - Saldo devedor atual (considerando juros compostos e IOF)
        - Valor total do IOF
        """,
    ),
    update=extend_schema(
        tags=["Loans"],
        summary="Atualizar empréstimo completo",
        description="""
        Atualiza todos os campos de um empréstimo.

        **Restrições:**
        - Campos críticos (`amount`, `interest_rate`, `bank`, `owner`)
          ficam bloqueados para edição se o empréstimo já possui
          pagamentos associados.
        """,
    ),
    partial_update=extend_schema(
        tags=["Loans"],
        summary="Atualizar empréstimo parcialmente",
        description="""
        Atualiza campos específicos de um empréstimo.

        **Restrições:**
        - Campos críticos (`amount`, `interest_rate`, `bank`, `owner`)
          ficam bloqueados para edição se o empréstimo já possui
          pagamentos associados.
        """,
    ),
    destroy=extend_schema(
        tags=["Loans"],
        summary="Excluir empréstimo",
        description=(
            "Exclui um empréstimo. Apenas empréstimos sem pagamentos "
            "podem ser excluídos."
        ),
    ),
)
class LoanViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        """Filter loans to only show those owned by the authenticated user."""
        queryset = Loan.objects.filter(owner=self.request.user)
        # Prefetch payments to avoid N+1 queries when calculating totals
        queryset = queryset.prefetch_related("payments")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return LoanListSerializer
        return LoanSerializer
