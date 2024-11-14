from datetime import datetime, timedelta, timezone

from django.test import override_settings
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
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


class UserProfileUnauthorizedAccessTests(APITestCase):
    def test_unauthorized_access(self):
        url = reverse("clothes_shop:user-profile")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # 認証なしでプロフィール取得を試みる

        data = {"name": "Unauthorized User"}
        response = self.client.patch(url, data)
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )  # 認証なしでプロフィール更新を試みる


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

        response = self.client.post(url, {"check_admin": False})
