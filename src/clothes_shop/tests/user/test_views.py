from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import timedelta, datetime, timezone
from rest_framework_simplejwt.tokens import AccessToken

from clothes_shop.models.user import User


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
    def test_signup_success(self):
        url = reverse("clothes_shop:user-signup")
        signup_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        with patch("clothes_shop.views.user_views.stripe_service.create_customer") as mock_create_customer:
            mock_create_customer.return_value = "cus_mocked_id"

            response = self.client.post(url, signup_data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn("message", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["name"], signup_data["name"])
        self.assertEqual(response.data["user"]["email"], signup_data["email"])
        self.assertEqual(response.data["user"]["role"], "registered")
        self.assertFalse(response.data["user"]["is_active"])

        user = User.objects.get(email=signup_data["email"])
        self.assertEqual(user.name, signup_data["name"])
        self.assertEqual(user.role, "registered")
        self.assertFalse(user.is_active)

    @patch("clothes_shop.views.user_views.stripe_service.create_customer")
    def test_signup_stripe_failure(self, mock_create_customer):
        mock_create_customer.side_effect = Exception("Stripe API error")
        url = reverse("clothes_shop:user-signup")
        signup_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepassword123"
        }

        response = self.client.post(url, signup_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Stripeの顧客登録に失敗しました。")
