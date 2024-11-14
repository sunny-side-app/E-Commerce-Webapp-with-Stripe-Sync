from datetime import datetime, timezone

from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from clothes_shop.models.user import User


class CheckAccessAndAdminViewTests(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")
        # 通常ユーザーの作成
        self.user = User.objects.create(
            name=fake.name(),
            stripe_customer_id="hogehoge1",
            email=fake.email(),
            role="registered",
            email_validated_at=datetime.now(timezone.utc),
            address=fake.address(),
            date_joined=datetime.now(timezone.utc),
            is_active=True,
            is_staff=False,
        )

        # 管理者ユーザーの作成
        self.admin_user = User.objects.create_user(
            name=fake.name(),
            stripe_customer_id="hogehoge2",
            email=fake.email(),
            role="registered",
            email_validated_at=datetime.now(timezone.utc),
            address=fake.address(),
            date_joined=datetime.now(timezone.utc),
            is_active=True,
            is_staff=True,
        )

    def get_access_token(self, user):
        return str(AccessToken.for_user(user))

    def test_access_with_valid_token(self):
        """=Falseのときのテスト"""
        url = reverse("clothes_shop:check_access_and_admin")
        access_token = self.get_access_token(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"], True)

    def test_admin_access_with_valid_token(self):
        url = reverse("clothes_shop:check_access_and_admin")
        access_token = self.get_access_token(self.admin_user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(url, {"check_admin": True})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["result"], True)

    def test_non_admin_access_with_check_admin_true(self):
        url = reverse("clothes_shop:check_access_and_admin")
        access_token = self.get_access_token(self.user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(url, {"check_admin": True})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["result"], False)
        self.assertEqual(response.data["message"], "管理者権限が必要です")

    def test_access_without_token(self):
        url = reverse("clothes_shop:check_access_and_admin")
        self.client.post(url, {"check_admin": False})
