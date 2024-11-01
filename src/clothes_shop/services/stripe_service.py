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

    def create_product(self, name: string, price: int) -> string:
        product: stripe.Product = stripe.Product.create(name=name)
        stripe.Price.create(
            product=product.id,
            unit_amount=price,
            tax_behavior="exclusive",
            currency="jpy",
        )
        return product.id

    def update_product(self, product_id: str, newName: str | None, newPrice: int | None) -> None:
        if newName is None and newPrice is None:
            return None
        if newName is not None:
            stripe.Product.modify(id=product_id, name=newName)
        if newPrice is not None:
            resp: stripe.ListObject[stripe.Price] = stripe.Price.list(
                active=True, product=product_id
            )
            for price in resp.data:
                stripe.Price.modify(price.id, active=False)
            stripe.Price.create(
                product=product_id,
                unit_amount=newPrice,
                tax_behavior="exclusive",
                currency="jpy",
            )
        return None

    def get_product(self, product_id: str) -> stripe.Product | None:
        product = stripe.Product.retrieve(product_id)
        return product if product.active is True else None

    def __get_price(self, product_id: str) -> stripe.Price:
        resp: stripe.ListObject[stripe.Price] = stripe.Price.list(active=True, product=product_id)
        price: stripe.Price = resp.data[0]
        return price

    def delete_product(self, id: string) -> None:
        # 製品登録時にpriceオブジェクトを生成すると、APIリクエストでは物理削除できない。
        # active=Falseにすることで、archivedにする。（論理削除）
        stripe.Product.modify(id, active=False)
        return None
