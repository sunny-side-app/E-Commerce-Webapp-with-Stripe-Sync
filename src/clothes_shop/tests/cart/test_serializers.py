import random
from datetime import datetime, timedelta

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
from clothes_shop.serializers import (
    BrandSerializer,
    CartItemSerializer,
    ClothesTypeSerializer,
    ProductSerializer,
    SizeSerializer,
    TargetSerializer,
    UserSerializer,
)


class CartItemAndRelatedSerializerTest(TestCase):

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
        self.productSerializer = ProductSerializer(self.product)
        self.sizeSerializer = SizeSerializer(self.size)
        self.targetSerializer = TargetSerializer(self.target)
        self.clothesTypeSerializer = ClothesTypeSerializer(self.cloth_type)
        self.brandSerializer = BrandSerializer(self.brand)
        self.userSerializer = UserSerializer(self.user)
        self.cartItemSerializer = CartItemSerializer(self.cartItem)

    def test_cartItem_serializer_contains_expected_fields(self):
        """シリアライザが期待されるフィールドを含んでいるかテスト"""
        self.assertEqual(
            set(self.cartItemSerializer.data.keys()),
            set(
                [
                    "user",
                    "product",
                    "quantity",
                ]
            ),
        )

    def test_cartItem_serializer_field_content(self):
        """シリアライザが正しい内容をシリアライズできるかテスト"""
        self.assertEqual(self.cartItemSerializer.data["user"], self.user.id)
        self.assertEqual(self.cartItemSerializer.data["product"]["id"], self.product.id)
        self.assertEqual(int(self.cartItemSerializer.data["quantity"]), self.quantity)

    def test_cartItem_serializer_valid_data(self):
        """シリアライザが正しいデータからオブジェクトを作成できるかテスト"""
        valid_data = {
            "user_pk": self.user.id,
            "product_pk": self.product.id,
            "quantity": random.randint(1, 5),
        }
        cartItemSerializerValid = CartItemSerializer(data=valid_data)
        self.assertTrue(cartItemSerializerValid.is_valid())
        cartItem = cartItemSerializerValid.save()
        self.assertEqual(cartItem.user.id, valid_data["user_pk"])
        self.assertEqual(cartItem.product.id, valid_data["product_pk"])
        self.assertEqual(cartItem.quantity, int(valid_data["quantity"]))

    def test_cartItem_serializer_invalid_data(self):
        """無効なデータがバリデーションエラーを引き起こすかテスト"""
        invalid_data = {
            "user_pk": self.user.id,
            "product_pk": self.product.id,
            "quantity": "error",
        }
        serializer = CartItemSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)
