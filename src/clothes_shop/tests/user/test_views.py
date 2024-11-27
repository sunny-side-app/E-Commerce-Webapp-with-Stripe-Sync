import stripe, os

from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import timedelta, datetime, timezone
from rest_framework_simplejwt.tokens import AccessToken

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from clothes_shop.models.user import User
from clothes_shop.services.email_service import EmailService


class UserAPITests(APITestCase):
    def test_CRUD_user(self):
        user_list_create_url = reverse("clothes_shop:user-list-create")
        initial_user_data = {
            "stripe_customer_id": "hogehoge",
            "email": "test@example.com",
            "password": "password",
            "name": "Test User",
            "role": "guest",
        }
        response_post = self.client.post(user_list_create_url, initial_user_data, format="json")
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)

        user_detail_url = reverse(
            "clothes_shop:user-detail", kwargs={"user_id": response_post.data["id"]}
        )
        response_get = self.client.get(user_detail_url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data["name"], initial_user_data["name"])

        updated_user_data = {
            "email": "test_updated@example.com",
            "password": "password_updated",
            "name": "Super Test User",
        }
        response_put = self.client.put(user_detail_url, updated_user_data, format="json")
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_put.data["name"], updated_user_data["name"])

        delete_user_data = {"id": response_get.data["id"]}
        response_delete = self.client.delete(user_detail_url, delete_user_data, format="json")
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)


class UserProfileViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", name="Test User", password="testpass", role="registered"
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile(self):
        url = reverse("clothes_shop:user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.user.name)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["role"], self.user.role)
        self.assertEqual(response.data["address"], self.user.address)
        self.assertEqual(response.data["is_active"], self.user.is_active)

    def test_update_user_profile(self):
        url = reverse("clothes_shop:user-profile")
        data = {"name": "Updated User", "address": "123 Updated Street"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Updated User")
        self.assertEqual(self.user.address, "123 Updated Street")


class UserProfileUnauthorizedAccessTests(APITestCase):
    def test_unauthorized_access(self):
        url = reverse("clothes_shop:user-profile")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # 認証なしでプロフィール取得を試みる

        data = {"name": "Unauthorized User"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # 認証なしでプロフィール更新を試みる

class TokenExpiryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="expiryuser@example.com",
            name="Expiry User",
            password="exppass",
            role="registered",
            is_active=True,
        )

    @override_settings(SIMPLE_JWT={'ACCESS_TOKEN_LIFETIME': timedelta(seconds=1)})
    def test_expired_token_access(self):
        token = AccessToken.for_user(self.user)  # トークンを発行
        token['exp'] = datetime.now(timezone.utc) - timedelta(seconds=1)  # 有効期限を過去に設定
        url = reverse('clothes_shop:user-profile')

        response = self.client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}") # 期限切れのトークンでリクエストを送信
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserSignupViewTests(APITestCase):
    def setUp(self):
        self.signup_url = reverse("clothes_shop:user-signup")
        self.user_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword123",
            "address": "123 Test Street",
        }

    def test_signup_success(self):
        with patch("clothes_shop.views.user_views.stripe_service.create_customer") as mock_create_customer:
            mock_create_customer.return_value = "cus_mocked_id"

            response = self.client.post(self.signup_url, self.user_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["name"], self.user_data["name"])
        self.assertEqual(response.data["user"]["email"], self.user_data["email"])
        self.assertEqual(response.data["user"]["address"], self.user_data["address"])

        user = User.objects.get(email=self.user_data["email"])
        self.assertEqual(user.name, self.user_data["name"])
        self.assertEqual(user.role, "registered")
        self.assertEqual(user.address, self.user_data["address"])
        self.assertFalse(user.is_active)

    @patch("clothes_shop.views.user_views.stripe_service.create_customer")
    def test_signup_duplicate_email_not_active(self, mock_create_customer):
        mock_create_customer.return_value = "cus_mocked_id"

        User.objects.create_user(
            email=self.user_data["email"],
            name=self.user_data["name"],
            password=self.user_data["password"],
            role="registered",
            is_active=False,
        )

        response = self.client.post(self.signup_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "メール認証が未完了です。メールを再送信したのでメールを確認し、リンクをクリックしてメール認証を完了させてください。")

    @patch("clothes_shop.views.user_views.stripe_service.create_customer")
    def test_signup_duplicate_email_active(self, mock_create_customer):
        mock_create_customer.return_value = "cus_mocked_id"

        User.objects.create_user(
            email=self.user_data["email"],
            name=self.user_data["name"],
            password=self.user_data["password"],
            role="registered",
            is_active=True,
        )

        response = self.client.post(self.signup_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "このメールアドレスは既に登録されています。")

    @patch("clothes_shop.services.email_service.EmailService.send_email")
    @patch("clothes_shop.services.stripe_service.StripeService.create_customer")
    def test_signup_stripe_failure(self, mock_create_customer, mock_send_email):
        mock_create_customer.side_effect = stripe.error.StripeError("API Error")
        mock_send_email.return_value = None 

        response = self.client.post(
            self.signup_url,
            data=self.user_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Stripeの顧客登録に失敗しました。")

    @patch("clothes_shop.services.email_service.EmailService.send_email")
    @patch("clothes_shop.views.user_views.stripe_service.create_customer")
    def test_signup_and_email_sent(self, mock_create_customer, mock_send_email):
        mock_create_customer.return_value = "cus_mocked_id"
        mock_send_email.return_value = None  # モックでメール送信成功をシミュレート

        response = self.client.post(self.signup_url, self.user_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertIn("user", response.data)

        user = User.objects.get(email=self.user_data["email"])
        self.assertEqual(user.name, self.user_data["name"])
        self.assertEqual(user.role, "registered")
        self.assertFalse(user.is_active)

        mock_send_email.assert_called_once_with(user, email_type="confirmation")

    
    @patch("clothes_shop.services.email_service.EmailService.send_email")
    def test_email_confirmation_link(self, mock_send_email):
        mock_send_email.return_value = None  # メール送信の成功をモック

        user = User.objects.create_user(
            email="testuser@example.com",
            name="Test User",
            password="securepassword123",
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = "test-token"

        base_url = os.getenv("CONFIRMATION_URL", "http://127.0.0.1:8081")
        expected_link = f"{base_url}/api/signup/account-confirm-email/{uid}/{token}/"

        email_service = EmailService()
        email_service.send_email(user, email_type="confirmation")

        mock_send_email.assert_called_once()  # 一度だけ呼び出されることを確認
        args, kwargs = mock_send_email.call_args  # 呼び出し時の引数を確認
        kwargs["message"] = f"Please click the following link to verify your email: {expected_link}"
        self.assertIn(expected_link, kwargs["message"])  # メールの本文にリンクが含まれることを確認
