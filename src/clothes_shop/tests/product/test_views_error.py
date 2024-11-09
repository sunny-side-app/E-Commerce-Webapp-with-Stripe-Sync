import logging
from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.models.product import Product
from clothes_shop.models.user import User

logger = logging.getLogger(__name__)


class ProductListViewTests(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")
        self.size_xl = Size.objects.create(name="XL")
        self.target_men = Target.objects.create(name="メンズ")
        self.cloth_type_shirt = ClothesType.objects.create(name="シャツ")
        self.brand_nike = Brand.objects.create(name="NIKE")
        self.one_week_ago = timezone.now() - timedelta(weeks=1)
        self.one_week_after = timezone.now() + timedelta(weeks=1)
        self.product = Product.objects.create(
            size=self.size_xl,
            target=self.target_men,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_nike,
            name="サイズXL",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_ago,
            stock_quantity=500,
            is_deleted=False,
        )
        self.user = User.objects.create(
            name=fake.name(),
            email=fake.email(),
            role="registered",
            email_validated_at=timezone.now(),
            address=fake.address(),
            date_joined=timezone.now(),
            is_active=True,
            is_staff=True,
        )
        self.list_url = reverse("clothes_shop:product-list")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_value_error(self):
        query_params = {"release_date": "hogehoge"}
        response = self.client.get(self.list_url, query_params=query_params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expectedMsg = (
            "フォーマットエラー。ISO format (e.g., 2023-09-30T10:00:00)を使用してください。"
        )
        self.assertEqual(response.data["message"], expectedMsg)

    def test_post_invalid_serializer(self):
        data = {
            "name": "test",
            "description": "hello",
            "price": 100.02,
            "stock_quantity": 10,
            "release_date": timezone.make_aware(datetime.strptime("2018-12-05", "%Y-%m-%d")),
            "size": self.size_xl.id,
            "target": self.target_men.id,
            "clothes_type": self.cloth_type_shirt.id,
            "brand": self.brand_nike.id,
            "categoryyyyyyyyy": "服",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductDetailViewTests(APITestCase):
    def setUp(self):
        self.size_xl = Size.objects.create(name="XL")
        self.target_men = Target.objects.create(name="メンズ")
        self.cloth_type_shirt = ClothesType.objects.create(name="シャツ")
        self.brand_nike = Brand.objects.create(name="NIKE")
        self.one_week_ago = timezone.now() - timedelta(weeks=1)
        self.one_week_after = timezone.now() + timedelta(weeks=1)
        self.product = Product.objects.create(
            size=self.size_xl,
            target=self.target_men,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_nike,
            name="サイズXL",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_ago,
            stock_quantity=500,
            is_deleted=False,
        )
        self.detail_url = reverse("clothes_shop:product-detail", kwargs={"pk": self.product.id})
        self.detail_url_not_found = reverse("clothes_shop:product-detail", kwargs={"pk": 0})

    def test_get_not_found(self):
        response = self.client.get(self.detail_url_not_found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
