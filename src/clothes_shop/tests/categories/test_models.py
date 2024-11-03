from django.test import TestCase

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target


class SizeModelTest(TestCase):

    def setUp(self):
        self.size = Size.objects.create(name="L")

    def test_size_creation(self):
        self.assertEqual(self.size.name, "L")

    def test_size_str_method(self):
        self.assertEqual(str(self.size), "L")


class TargetModelTest(TestCase):

    def setUp(self):
        self.target = Target.objects.create(name="レディース")

    def test_target_creation(self):
        self.assertEqual(self.target.name, "レディース")

    def test_target_str_method(self):
        self.assertEqual(str(self.target), "レディース")


class ClothesTypeModelTest(TestCase):

    def setUp(self):
        self.clothes_type = ClothesType.objects.create(name="ズボン")

    def test_clothes_type_creation(self):
        self.assertEqual(self.clothes_type.name, "ズボン")

    def test_clothes_type_str_method(self):
        self.assertEqual(str(self.clothes_type), "ズボン")


class BrandModelTest(TestCase):

    def setUp(self):
        self.brand = Brand.objects.create(name="UNIQLO")

    def test_brand_creation(self):
        self.assertEqual(self.brand.name, "UNIQLO")

    def test_brand_str_method(self):
        self.assertEqual(str(self.brand), "UNIQLO")
