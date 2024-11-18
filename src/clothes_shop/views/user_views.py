import logging
import stripe

from rest_framework import generics, permissions, status
from rest_framework.exceptions import APIException, NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from clothes_shop.models.user import User
from clothes_shop.serializers.user_serializers import (
    UserProfileSerializer,
    UserSerializer,
    UserSignupSerializer,
    ConfirmEmailSerializer,
    ResendConfirmationEmailSerializer
)
from clothes_shop.services.stripe_service import CustomerData, StripeService
from clothes_shop.services.email_service import EmailService

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
            
            user = serializer.save(stripe_customer_id=stripe_customer_id)

            try:
                EmailService.send_email(user, email_type="confirmation")
            except Exception as e:
                logger.error(f"確認メール送信失敗: {e}")
                return Response(
                        {"error": "確認メールの再送信に失敗しました。"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    ) 
        except stripe.error.StripeError as e:
            logger.error(f"Stripeエラー: {e}")
            raise ValidationError({"error": "Stripeの顧客登録に失敗しました。"})

        except ValidationError as e:
            logger.error(f"バリデーションエラー: {e}")
            raise ValidationError({"error": "入力データに不正があります。"})

        except Exception as e:
            logger.error(f"予期しないエラー: {e}")
            raise ValidationError({"error": "ユーザー登録中にエラーが発生しました。"})

    def create(self, request, *args, **kwargs):
        email = request.data.get("email")

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if not existing_user.is_active:
                try:
                    EmailService.send_email(existing_user, email_type="confirmation")
                    return Response(
                        {"error": "メール認証が未完了です。メールを再送信したのでメールを確認し、リンクをクリックしてメール認証を完了させてください。"},
                        status=status.HTTP_200_OK,
                    )
                except Exception as e:
                    logger.error(f"確認メール再送信失敗: {e}")
                    return Response(
                        {"error": "確認メールの再送信に失敗しました。"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            else:
                return Response(
                    {"error": "このメールアドレスは既に登録されています。"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        try:
            response = super().create(request, *args, **kwargs)
            response.data = {
                "message": "ユーザー登録が成功しました。メールを確認し、リンクをクリックしてメール認証を完了させてください。",
                "user": response.data,
            }
            return response
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"ユーザー登録時の予期せぬエラー: {e}")
            return Response(
                {"error": "ユーザー登録中にエラーが発生しました。"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResendConfirmationEmailView(generics.GenericAPIView):# サインアップ後に未認証ユーザーへ確認メールを送信するビュー(未使用)
    serializer_class = ResendConfirmationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"バリデーションエラー: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = serializer.validated_data["email"]
            user = User.objects.get(email=email)

            EmailService.send_email(user, email_type="confirmation")
            return Response({"message": "確認メールを送信しました。"}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            logger.error(f"ユーザーが見つかりません: {serializer.validated_data['email']}")
            return Response(
                {"error": "指定されたメールアドレスのユーザーが見つかりません。"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"メール送信失敗: {e}")
            return Response({"error": "メール送信に失敗しました。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

token_generator = PasswordResetTokenGenerator()

class EmailConfirmationView(generics.GenericAPIView):
    """
    メール認証リンクを処理するビュー。
    """
    serializer_class = ConfirmEmailSerializer

    def get(self, request, uidb64, token, *args, **kwargs):
        serializer = self.get_serializer(data={"uidb64": uidb64, "token": token})
        if not serializer.is_valid():
            logger.error(f"バリデーションエラー: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uidb64"]))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            logger.error(f"UIDデコードエラー: uidb64={uidb64}")
            return Response({"error": "無効なトークンです。"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logger.error(f"ユーザーが見つかりません: uid={uidb64}")
            return Response({"error": "無効なトークンです。"}, status=status.HTTP_404_NOT_FOUND)

        if not token_generator.check_token(user, serializer.validated_data["token"]):
            return Response({"error": "無効なトークンです。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user.is_active = True
            user.save()

            return Response({"message": "メール認証が完了しました。"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"メール認証中のエラー: {e}")
            return Response({"error": "予期せぬエラーが発生しました。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
