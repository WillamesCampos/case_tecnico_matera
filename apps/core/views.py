from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Health"],
        summary="Health Check",
        description=(
            "Verifica o status da API e retorna informações básicas "
            "sobre o serviço."
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "example": "credit-track",
                    },
                    "version": {"type": "string", "example": "0.6.3"},
                    "message": {"type": "string", "example": "API is running"},
                    "status": {"type": "string", "example": "ok"},
                },
            }
        },
    )
    def get(self, request):
        data = {
            "project_name": "credit-track",
            "version": "0.6.3",
            "message": "API is running",
            "status": "ok",
        }
        return Response(data, status=status.HTTP_200_OK)
