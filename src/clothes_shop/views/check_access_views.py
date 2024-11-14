import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class CheckAccessAndAdminView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        check_admin = request.data.get("check_admin")
        if check_admin is None:
            check_admin = False
        user = request.user
        if check_admin and not user.is_staff:
            return Response(
                {"message": "管理者権限が必要です", "result": False},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response({"result": True}, status=status.HTTP_200_OK)
