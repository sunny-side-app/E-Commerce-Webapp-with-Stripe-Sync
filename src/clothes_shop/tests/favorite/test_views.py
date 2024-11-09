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
    Favorite,
    Product,
    Size,
    Target,
    User,
)
from clothes_shop.serializers.user_interaction_serializers import FavoriteSerializer


class FavoriteListCreateViewTests(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")
        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")
        self.product1 = Product.objects.create(
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
        self.product2 = Product.objects.create(
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
            date_joined=timezone.now(),
            is_active=True,
            is_staff=True,
        )
        self.quantity = random.randint(1, 5)
        self.favorites = Favorite.objects.create(user=self.user, product=self.product1)
        self.list_url = reverse("clothes_shop:favorite-list-create")
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_favs_by_User(self):
        """
        ログインユーザーのfav情報を取得
        """
        response = self.client.get(self.list_url)
        favs = Favorite.objects.filter(user_id=self.user.id)
        serializer = FavoriteSerializer(favs, many=True)

        response_data = [
            {key: value for key, value in item.items()} for item in response.data["results"]
        ]
        serializer_data = [{key: value for key, value in item.items()} for item in serializer.data]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, serializer_data)

    def test_create_new_Fav(self):
        """
        新たにproductにいいねする
        """
        data = {
            "user_id": self.user.id,
            "product_id": self.product2.id,
            "fav": True,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fav"], True)

        self.assertEqual(
            response.data["message"],
            f"product_id:{self.product2.id}をFavoriteに追加しました。",
        )

    def test_delete_Fav(self):
        """
        いいねをはずす
        """
        data = {"user_id": self.user.id, "product_id": self.product1.id, "fav": False}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fav"], False)

        self.assertEqual(
            response.data["message"],
            f"product_id:{self.product1.id}をFavoriteから削除しました。",
        )