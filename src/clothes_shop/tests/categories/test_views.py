from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.serializers import (
    BrandSerializer,
    ClothesTypeSerializer,
    SizeSerializer,
    TargetSerializer,
)


class CategoryListTests(APITestCase):

    def setUp(self):
        # 各カテゴリのテストデータを作成
        self.size = Size.objects.create(name="L")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")

        # CategoryListView のURLを取得
        self.category_list_url = reverse("clothes_shop:category-list")

    def test_get_category_list(self):
        # GETリクエストを送信
        response = self.client.get(self.category_list_url)

        # それぞれのカテゴリデータをシリアライズ
        sizes = Size.objects.all()
        targets = Target.objects.all()
        clothes_types = ClothesType.objects.all()
        brands = Brand.objects.all()

        size_serializer = SizeSerializer(sizes, many=True)
        target_serializer = TargetSerializer(targets, many=True)
        clothes_type_serializer = ClothesTypeSerializer(clothes_types, many=True)
        brand_serializer = BrandSerializer(brands, many=True)

        # 期待されるデータ
        expected_data = {
            "sizeCatgory": size_serializer.data,
            "targetCatgory": target_serializer.data,
            "typeCatgory": clothes_type_serializer.data,
            "brandCatgory": brand_serializer.data,
        }

        # ステータスコードとレスポンスデータの検証
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
