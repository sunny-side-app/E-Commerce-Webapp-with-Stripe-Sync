import unittest

from rest_framework.test import APITestCase

from clothes_shop.services.stripe_service import StripeService

# ファイルに変更があってテストが必要な場合だけTrueに変更する
# テストが終了したらFalseに戻すこと
isFileChanged: bool = False


@unittest.skipUnless(
    isFileChanged,
    "テストで登録した製品データをテスト内で物理削除できないので、変更があったとき以外は実行しない。",
)
class ProductTests(APITestCase):
    def setUp(self):
        self.stripe_service = StripeService()

    def test_CRUD(self):
        price_data = {"currency": "jpy", "tax_behavior": "inclusive", "unit_amount": 2500}
        test_product = {
            "name": "Test Cloth",
            "active": True,
            "description": "test description",
            "metadata": {},
            "default_price_data": price_data,
            "images": [],
            "marketing_features": [],
            "package_dimensions": None,
            "shippable": True,
            "statement_descriptor": "hogehoge",
            "tax_code": "txcd_99999999",
            "unit_label": "着",
            "url": "example.com",
        }
        product = self.stripe_service.create_product(test_product)
        self.assertEqual(test_product["name"], product.name)

        test_product_updated = {"name": "Test Cloth Updated"}
        product_updated = self.stripe_service.update_product(product.id, test_product_updated)
        self.assertEqual(test_product_updated["name"], product_updated.name)

        product_retrieved = self.stripe_service.retrieve_product(product_updated.id)
        self.assertEqual(test_product_updated["name"], product_retrieved.name)
        self.assertEqual(test_product["description"], product_retrieved.description)

        product_deleted = self.stripe_service.delete_product(product_retrieved.id)
        self.assertEqual(product_deleted["id"], product_retrieved.id)
        self.assertFalse(product_deleted["active"])
