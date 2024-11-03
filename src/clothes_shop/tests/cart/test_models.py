import random
from datetime import datetime

from django.test import TestCase
from django.utils import timezone
from faker import Faker

from clothes_shop.models import (
    Brand,
    CartItem,
    ClothesType,
    Product,
    Size,
    Target,
    User,
)


class CartModelTest(TestCase):

    def setUp(self):
        fake = Faker("ja_JP")
        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")
        self.product = Product.objects.create(
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
        )
        self.user = User.objects.create(
            name=fake.name(),
            email_address=fake.email(),
            role="registered",
            email_validated_at=timezone.now(),
            address=fake.address(),
        )
        self.quantity = random.randint(1, 5)
        self.cartItem = CartItem.objects.create(
            user=self.user, product=self.product, quantity=self.quantity
        )

    def test_cartItem_creation(self):
        self.assertEqual(self.cartItem.user, self.user)
        self.assertEqual(self.cartItem.quantity, self.quantity)
