from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            "project_name": "credit-track",
            "version": "0.1.0",
            "message": "API is running",
            "status": "ok"
        }
        return Response(data, status=status.HTTP_200_OK)