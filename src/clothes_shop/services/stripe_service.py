import logging
import os
import string
from pathlib import Path

import environ
import stripe

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))

logger = logging.getLogger(__name__)


class StripeService:
    def __init__(self):
        stripe.api_key = env("STRIPE_SECRET_KEY")

    def create_product(self, product_data: stripe.Product):
        return stripe.Product.create(**product_data)

    def update_product(self, id: string, product_data: stripe.Product):
        return stripe.Product.modify(id, **product_data)

    def get_product(self, id: string):
        return stripe.Product.retrieve(id)

    def delete_product(self, id: string):
        # 製品登録時にpriceオブジェクトを生成すると、APIリクエストでは物理削除できなくなる。
        # active=Falseにすることで、archivedにできる。（論理削除）
        return stripe.Product.modify(id, active=False)
