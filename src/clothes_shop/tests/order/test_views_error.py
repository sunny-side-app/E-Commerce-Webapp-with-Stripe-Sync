import random
from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clothes_shop.models import (
    Brand,
    CartItem,
    ClothesType,
    Order,
    OrderItem,
    Product,
    Size,
    Target,
    User,
)
from clothes_shop.serializers.order_serializers import OrderSerializer


class OrderTests(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")
        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")
        self.product_login = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ",
            description="てすと",
            category="服",
            price=100,
            release_date=timezone.make_aware(datetime.strptime("2018-12-05", "%Y-%m-%d")),
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_cart",
        )
        self.product_other = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="カートに入っていない商品",
            description="てすと",
            category="服",
            price=100,
            release_date=timezone.make_aware(datetime.strptime("2018-12-05", "%Y-%m-%d")),
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_new",
        )
        self.user_login = User.objects.create(
            stripe_customer_id="user_login",
            name=fake.name(),
            email=fake.email(),
            role="registered",
            email_validated_at=timezone.now(),
            address=fake.address(),
            date_joined=timezone.now(),
            is_active=True,
            is_staff=True,
        )
        self.user_other = User.objects.create(
            stripe_customer_id="user_other",
            name=fake.name(),
            email=fake.email(),
            role="registered",
            email_validated_at=timezone.now(),
            address=fake.address(),
            date_joined=timezone.now(),
            is_active=True,
            is_staff=False,
        )
        status_choices = [
            "pending",
            "confirmed",
            "shipped",
            "delivered",
            "cancelled",
            "returned",
            "failed",
            "completed",
        ]
        # ログインユーザーオーダーを作成
        self.order_other = Order.objects.create(
            user=self.user_login,
            order_status=random.choice(status_choices),
            total_price=0,
            order_date=timezone.now(),
        )
        self.order_item = OrderItem.objects.create(
            order=self.order_other,
            product=self.product_login,
            quantity=random.randint(1, 5),
            unit_price=random.randint(100, 1000),
        )
        self.order_other.total_price = self.order_item.quantity * self.order_item.unit_price
        self.order_other.save()

        # 他ユーザーオーダーを作成
        self.order_other = Order.objects.create(
            user=self.user_other,
            order_status=random.choice(status_choices),
            total_price=0,
            order_date=timezone.now(),
        )
        self.order_item = OrderItem.objects.create(
            order=self.order_other,
            product=self.product_other,
            quantity=random.randint(1, 5),
            unit_price=random.randint(100, 1000),
        )
        self.order_other.total_price = self.order_item.quantity * self.order_item.unit_price
        self.order_other.save()
        refresh = RefreshToken.for_user(self.user_other)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.list_url = reverse("clothes_shop:order-list-create")

    def test_get_allOrders_auth_error(self):
        response = self.client.get(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
