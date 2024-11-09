from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.models.product import Product
from clothes_shop.models.user import User
from clothes_shop.serializers.product_serializers import ProductSerializer
from clothes_shop.services.stripe_service import StripeService

stripe_service = StripeService()


class ProductTests(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")

        self.create_product_patcher = patch(
            "clothes_shop.services.stripe_service.StripeService.create_product",
            return_value="test",
        )
        self.update_product_patcher = patch(
            "clothes_shop.services.stripe_service.StripeService.update_product", return_value=None
        )
        self.delete_product_patcher = patch(
            "clothes_shop.services.stripe_service.StripeService.delete_product", return_value=None
        )

        self.mock_create_product = self.create_product_patcher.start()
        self.mock_update_product = self.update_product_patcher.start()
        self.mock_delete_product = self.delete_product_patcher.start()

        self.addCleanup(self.create_product_patcher.stop)
        self.addCleanup(self.update_product_patcher.stop)
        self.addCleanup(self.delete_product_patcher.stop)

        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")
        self.one_week_ago = timezone.now() - timedelta(weeks=1)
        self.one_week_after = timezone.now() + timedelta(weeks=1)
        self.product_1 = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ１",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_1",
        )
        self.product_2 = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ２",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_2",
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
        self.detail_url = reverse("clothes_shop:product-detail", kwargs={"pk": self.product_1.id})
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_individual(self):
        response = self.client.get(self.detail_url)
        product = Product.objects.get(pk=self.product_1.id)
        serializer = ProductSerializer(product, many=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_cloth(self):
        data = {
            "name": "test",
            "description": "hello",
            "price": 1200,
            "stock_quantity": 10,
            "release_date": self.one_week_ago,
            "size_pk": self.size.id,
            "target_pk": self.target.id,
            "clothes_type_pk": self.cloth_type.id,
            "brand_pk": self.brand.id,
            "category": "服",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product_created = Product.objects.get(id=response.data["id"])
        self.assertEqual(Product.objects.count(), 3)
        self.assertEqual(product_created.name, "test")
        self.assertEqual(product_created.description, "hello")
        self.assertEqual(float(product_created.price), 1200)
        self.assertEqual(product_created.stock_quantity, 10)
        self.assertEqual(product_created.release_date, self.one_week_ago)
        self.assertEqual(product_created.size.name, "XL")
        self.assertEqual(product_created.target.name, "メンズ")
        self.assertEqual(product_created.clothes_type.name, "シャツ")
        self.assertEqual(product_created.brand.name, "NIKE")
        self.assertEqual(product_created.category, "服")

    def test_update_cloth(self):
        data = {
            "name": "updated_product",
            "description": "hello",
            "price": 9000,
            "stock_quantity": 1780,
            "release_date": self.one_week_ago,
            "size": self.size.name,
            "target": self.target.name,
            "clothes_type": self.cloth_type.name,
            "brand": self.brand.name,
            "category": "服",
        }
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_1.refresh_from_db()
        self.assertEqual(self.product_1.name, "updated_product")
        self.assertEqual(self.product_1.description, "hello")
        self.assertEqual(self.product_1.price, 9000)
        self.assertEqual(self.product_1.stock_quantity, 1780)
        self.assertEqual(self.product_1.release_date, self.one_week_ago)
        self.assertEqual(self.product_1.size.name, "XL")
        self.assertEqual(self.product_1.target.name, "メンズ")
        self.assertEqual(self.product_1.clothes_type.name, "シャツ")
        self.assertEqual(self.product_1.brand.name, "NIKE")
        self.assertEqual(self.product_1.category, "服")

    def test_delete_cloth(self):
        product_count_total = 2
        self.assertEqual(Product.objects.count(), product_count_total)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), product_count_total - 1)
