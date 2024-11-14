import logging

from rest_framework import generics, permissions, status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from clothes_shop.models.user import User
from clothes_shop.serializers.user_serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from clothes_shop.services.stripe_service import CustomerData, StripeService

logger = logging.getLogger(__name__)
stripe_service = StripeService()


def get_user(user_id) -> User:
    try:
        user = User.objects.get(pk=user_id)
        return user
    except User.DoesNotExist:
        errMsg = f"指定されたID {user_id} に紐づくユーザーが存在しません。"
        logger.error(errMsg)
        raise NotFound(detail=errMsg)
    except Exception as e:
        errMsg = f"想定外のエラーが発生しました: {str(e)}"
        logger.error(errMsg)
        raise APIException(detail=errMsg)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            customerData = CustomerData(name=request.data["name"], email=request.data["email"])
            stripe_customer_id = stripe_service.create_customer(customerData)
            serializer.save(stripe_customer_id=stripe_customer_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.error(e.detail)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        user = get_user(kwargs.get("user_id"))
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = get_user(kwargs.get("user_id"))
        serializer = UserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        customerData = CustomerData(name=request.data["name"], email=request.data["email"])
        stripe_service.update_customer(user.stripe_customer_id, customerData)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = get_user(kwargs.get("user_id"))
        stripe_service.delete_customer(user.stripe_customer_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


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
