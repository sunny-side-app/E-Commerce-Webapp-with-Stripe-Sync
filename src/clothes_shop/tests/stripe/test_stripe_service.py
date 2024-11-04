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
class StripeServiceTests(APITestCase):
    def setUp(self):
        self.stripe_service = StripeService()

    def test_CRUD(self):
        price = 2500
        product_name = "Test Cloth"
        product_id = self.stripe_service.create_product(product_name, price)

        product_name_updated = "Test Cloth Updated"
        price_updated = 10000
        self.stripe_service.update_product(product_id, product_name_updated, price_updated)

        product = self.stripe_service.get_product(product_id)
        self.assertEqual(product_name_updated, product.name)

        self.stripe_service.delete_product(product_id)
        product_deleted = self.stripe_service.get_product(product_id)
        self.assertIsNone(product_deleted)
