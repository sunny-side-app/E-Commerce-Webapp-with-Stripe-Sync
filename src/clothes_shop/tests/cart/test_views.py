import random
from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from clothes_shop.models import (
    Brand,
    CartItem,
    ClothesType,
    Product,
    Size,
    Target,
    User,
)
from clothes_shop.serializers.cart_serializers import CartItemSerializer


class CartItemTests(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")
        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")
        self.product_cart = Product.objects.create(
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
        self.product_new = Product.objects.create(
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
        self.user = User.objects.create(
            name=fake.name(),
            email=fake.email(),
            role="registered",
            email_validated_at=timezone.now(),
            address=fake.address(),
        )
        self.quantity = random.randint(1, 5)
        self.cartItem = CartItem.objects.create(
            user=self.user, product=self.product_cart, quantity=self.quantity
        )
        self.list_url = reverse("clothes_shop:cartitem-list-create")

    def test_get_cartItems_by_User(self):
        response = self.client.get(self.list_url, {"user": self.user.id})
        cartItems = CartItem.objects.filter(user_id=self.user.id)
        serializer = CartItemSerializer(cartItems, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_cart_item_with_quantity(self):
        """
        指定されたquantityでカートアイテムを作成
        """
        data = {
            "user_id": self.user.id,
            "product_id": self.product_new.id,
            "quantity": 3,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cart_item"]["quantity"], 3)
        self.assertEqual(
            response.data["message"],
            f"指定のproduct_id:{self.product_new.id}はカートに新規登録されました。",
        )

    def test_create_cart_item_without_quantity(self):
        """
        quantityが指定されていない場合、デフォルトで1にする
        """
        data = {
            "user_id": self.user.id,
            "product_id": self.product_new.id,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cart_item"]["quantity"], 1)
        self.assertEqual(
            response.data["message"],
            f"指定のproduct_id:{self.product_new.id}はカートに新規登録されました。",
        )

    def test_update_cart_item_quantity(self):
        """
        既存のカートアイテムの数量を更新する
        """
        # 事前にカートアイテムを作成
        cart_item = CartItem.objects.create(user=self.user, product=self.product_new, quantity=2)

        data = {
            "user_id": self.user.id,
            "product_id": cart_item.product.id,
            "quantity": 5,
        }
        response = self.client.post(self.list_url, data, format="json")
        cart_item.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cart_item.quantity, 5)
        self.assertEqual(
            response.data["message"],
            f"指定のproduct_id:{cart_item.product.id}の数量を変更しました。",
        )

    def test_increment_cart_item_quantity(self):
        """
        quantityが指定されていない場合、既存のカートアイテムの数量を1増加させる
        """
        # 事前にカートアイテムを作成
        cart_item = CartItem.objects.create(user=self.user, product=self.product_new, quantity=2)
        previous_quantity = cart_item.quantity
        data = {
            "user_id": self.user.id,
            "product_id": cart_item.product.id,
        }
        response = self.client.post(self.list_url, data, format="json")
        # データベースから最新のcart_itemを取得
        cart_item.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cart_item.quantity, previous_quantity + 1)
        self.assertEqual(
            response.data["message"],
            f"指定のproduct_id:{self.product_new.id}の数量を1増加しました。",
        )

    def test_delete_cart_item(self):
        """
        既存のカートアイテムを削除する
        """
        # 事前にカートアイテムを作成
        cart_item = CartItem.objects.create(user=self.user, product=self.product_new, quantity=1)
        data = {
            "user_id": self.user.id,
            "product_id": cart_item.product.id,
        }
        response = self.client.delete(self.list_url, data, format="json")

        cart_item_exists = CartItem.objects.filter(
            user_id=self.user.id, product_id=self.product_new.id
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cart_item_exists, False)
        self.assertEqual(
            response.data["message"],
            f"product_id:{self.product_new.id}をカートから削除しました。",
        )
        self.assertEqual(
            response.data["result"],
            True,
        )
