from django.test import TestCase

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.serializers.attributes_serializers import (
    BrandSerializer,
    ClothesTypeSerializer,
    SizeSerializer,
    TargetSerializer,
)


class SizeSerializerTest(TestCase):
    def setUp(self):
        self.size = Size.objects.create(name="XL")
        self.size_serializer = SizeSerializer(self.size)

    def test_size_serializer_contains_expected_fields(self):
        # 項目名の一致を確認
        self.assertEqual(
            set(self.size_serializer.data.keys()), {"id", "name", "created_at", "updated_at"}
        )

    def test_size_serializer_field_content(self):
        # シリアライザの値と実際の値を比較
        self.assertEqual(self.size_serializer.data["name"], self.size.name)


class TargetSerializerTest(TestCase):
    def setUp(self):
        self.target = Target.objects.create(name="メンズ")
        self.target_serializer = TargetSerializer(self.target)

    def test_target_serializer_contains_expected_fields(self):
        """Targetシリアライザが期待されるフィールドを含んでいるかテスト"""
        self.assertEqual(
            set(self.target_serializer.data.keys()), {"id", "name", "created_at", "updated_at"}
        )

    def test_target_serializer_field_content(self):
        """Targetシリアライザが正しい内容をシリアライズできるかテスト"""
        self.assertEqual(self.target_serializer.data["name"], self.target.name)


class ClothesTypeSerializerTest(TestCase):
    def setUp(self):
        self.clothes_type = ClothesType.objects.create(name="シャツ")
        self.clothes_type_serializer = ClothesTypeSerializer(self.clothes_type)

    def test_clothes_type_serializer_contains_expected_fields(self):
        """ClothesTypeシリアライザが期待されるフィールドを含んでいるかテスト"""
        self.assertEqual(
            set(self.clothes_type_serializer.data.keys()),
            {"id", "name", "created_at", "updated_at"},
        )

    def test_clothes_type_serializer_field_content(self):
        """ClothesTypeシリアライザが正しい内容をシリアライズできるかテスト"""
        self.assertEqual(self.clothes_type_serializer.data["name"], self.clothes_type.name)


class BrandSerializerTest(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="NIKE")
        self.brand_serializer = BrandSerializer(self.brand)

    def test_brand_serializer_contains_expected_fields(self):
        """Brandシリアライザが期待されるフィールドを含んでいるかテスト"""
        self.assertEqual(
            set(self.brand_serializer.data.keys()), {"id", "name", "created_at", "updated_at"}
        )

    def test_brand_serializer_field_content(self):
        """Brandシリアライザが正しい内容をシリアライズできるかテスト"""
        self.assertEqual(self.brand_serializer.data["name"], self.brand.name)
