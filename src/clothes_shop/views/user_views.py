import logging

from rest_framework import generics, permissions, status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models.user import User
from clothes_shop.serializers.user_serializers import (
    UserProfileSerializer,
    UserSerializer,
    UserSignupSerializer,
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

class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        try:
            customer_data = CustomerData(
                name=serializer.validated_data["name"],
                email=serializer.validated_data["email"],
            )
            stripe_customer_id = stripe_service.create_customer(customer_data)
            
            serializer.save(stripe_customer_id=stripe_customer_id)
        except Exception as e:
            api_exception = APIException(detail="Stripeの顧客登録に失敗しました。")
            api_exception.status_code = 500
            raise api_exception
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            "message": "ユーザー登録が成功しました。メールを確認してください。",
            "user": response.data,
        }
        return response