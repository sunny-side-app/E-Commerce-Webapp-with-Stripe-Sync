from datetime import datetime, timedelta, timezone

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from clothes_shop.models.user import User


class TokenAuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="authuser@example.com",
            name="Auth User",
            password="authpass",
            role="registered",
            is_active=True,
        )

    def test_token_obtain(self):
        url = reverse("clothes_shop:token_obtain_pair")
        response = self.client.post(url, {"email": "authuser@example.com", "password": "authpass"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class TokenExpiryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="expiryuser@example.com",
            name="Expiry User",
            password="exppass",
            role="registered",
            is_active=True,
        )

    @override_settings(SIMPLE_JWT={"ACCESS_TOKEN_LIFETIME": timedelta(seconds=1)})
    def test_expired_token_access(self):
        token = AccessToken.for_user(self.user)  # トークンを発行
        token["exp"] = datetime.now(timezone.utc) - timedelta(seconds=1)  # 有効期限を過去に設定
        url = reverse("clothes_shop:user-profile")

        response = self.client.get(
            url, HTTP_AUTHORIZATION=f"Bearer {token}"
        )  # 期限切れのトークンでリクエストを送信
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
