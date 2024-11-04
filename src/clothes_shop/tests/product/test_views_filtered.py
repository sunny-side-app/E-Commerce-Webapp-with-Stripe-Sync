from datetime import timedelta

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.models.product import Product
from clothes_shop.serializers.product_serializers import ProductSerializer


class ProductTests(APITestCase):
    def setUp(self):
        self.size_m = Size.objects.create(name="M")
        self.size_xl = Size.objects.create(name="XL")
        self.target_mens = Target.objects.create(name="メンズ")
        self.target_womens = Target.objects.create(name="レディース")
        self.cloth_type_shirt = ClothesType.objects.create(name="シャツ")
        self.cloth_type_pants = ClothesType.objects.create(name="パンツ")
        self.brand_nike = Brand.objects.create(name="NIKE")
        self.brand_adidas = Brand.objects.create(name="ADIDAS")
        one_week_ago = timezone.now() - timedelta(weeks=1)
        self.one_week_after = timezone.now() + timedelta(weeks=1)
        self.product_0 = Product.objects.create(
            size=self.size_m,
            target=self.target_mens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_nike,
            name="論理削除された製品",
            description="てすと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=True,
            stripe_product_id="product_0",
        )
        self.product_1 = Product.objects.create(
            size=self.size_m,
            target=self.target_mens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_nike,
            name="未来のリリース日の製品",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_1",
        )
        self.product_2 = Product.objects.create(
            size=self.size_xl,
            target=self.target_mens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_nike,
            name="サイズXL",
            description="てすと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_2",
        )
        self.product_3 = Product.objects.create(
            size=self.size_m,
            target=self.target_womens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_nike,
            name="レディース",
            description="てすと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_3",
        )
        self.product_4 = Product.objects.create(
            size=self.size_m,
            target=self.target_mens,
            clothes_type=self.cloth_type_pants,
            brand=self.brand_nike,
            name="服の種類がパンツ",
            description="てすと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_4",
        )
        self.product_5 = Product.objects.create(
            size=self.size_m,
            target=self.target_mens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_adidas,
            name="アディダス",
            description="てすと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_5",
        )
        self.product_6 = Product.objects.create(
            size=self.size_m,
            target=self.target_mens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_adidas,
            name="テスト用につくったキーワード服１",
            description="てすと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_6",
        )
        self.product_7 = Product.objects.create(
            size=self.size_m,
            target=self.target_mens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_adidas,
            name="商品説明にkeyword",
            description="てすキーワードと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_7",
        )
        self.product_8 = Product.objects.create(
            size=self.size_m,
            target=self.target_womens,
            clothes_type=self.cloth_type_shirt,
            brand=self.brand_adidas,
            name="ブランドがアディダスでレディース",
            description="てすと",
            category="服",
            price=100,
            release_date=one_week_ago,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_8",
        )
        self.list_url = reverse("clothes_shop:product-list")

    def test_get_filtered_list_no_filters(self):
        response = self.client.get(self.list_url)
        product = Product.objects.filter(is_deleted=False, release_date__lt=timezone.now())
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_is_deleted(self):
        response = self.client.get(self.list_url, {"is_deleted": True})
        product = Product.objects.filter(is_deleted=True)
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_release_date(self):
        response = self.client.get(
            self.list_url, {"release_date": (self.one_week_after).isoformat()}
        )
        product = Product.objects.filter(is_deleted=False, release_date__lt=self.one_week_after)
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_invalid_date(self):
        response = self.client.get(self.list_url, {"release_date": "invalid_date"})
        product = Product.objects.filter(is_deleted=False, release_date__lt=self.one_week_after)
        ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_filtered_list_by_size(self):
        response = self.client.get(self.list_url, {"size[]": [self.size_xl.id]})
        product = Product.objects.filter(
            size=self.size_xl, is_deleted=False, release_date__lt=timezone.now()
        )
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_by_target(self):
        response = self.client.get(self.list_url, {"target[]": [self.target_mens.id]})
        product = Product.objects.filter(
            target=self.target_mens, is_deleted=False, release_date__lt=timezone.now()
        )
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_by_clothes_type(self):
        response = self.client.get(self.list_url, {"clothes_type[]": [self.cloth_type_pants.id]})
        product = Product.objects.filter(
            clothes_type=self.cloth_type_pants, is_deleted=False, release_date__lt=timezone.now()
        )
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_by_brand(self):
        response = self.client.get(self.list_url, {"brand[]": [self.brand_nike.id]})
        product = Product.objects.filter(
            brand=self.brand_nike, is_deleted=False, release_date__lt=timezone.now()
        )
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_by_combined_filters(self):
        response = self.client.get(
            self.list_url,
            {
                "size[]": [self.size_m.id],
                "target[]": [self.target_mens.id],
                "clothes_type[]": [self.cloth_type_shirt.id],
            },
        )
        product = Product.objects.filter(
            size=self.size_m,
            target=self.target_mens,
            clothes_type=self.cloth_type_shirt,
            is_deleted=False,
            release_date__lt=timezone.now(),
        )
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_by_keyword_in_name_or_description(self):
        response = self.client.get(
            self.list_url,
            {"keyword": "キーワード"},
        )
        product = Product.objects.filter(
            (Q(name__icontains="キーワード") | Q(description__icontains="キーワード")),
            is_deleted=False,
            release_date__lt=timezone.now(),
        )
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_filtered_list_by_multiple_filters(self):
        response = self.client.get(
            self.list_url,
            {
                "target[]": [self.target_womens.id],
                "brand[]": [self.brand_adidas.id],
            },
        )
        product = Product.objects.filter(
            target=self.target_womens,
            brand=self.brand_adidas,
            is_deleted=False,
            release_date__lt=timezone.now(),
        )
        serializer = ProductSerializer(product, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
