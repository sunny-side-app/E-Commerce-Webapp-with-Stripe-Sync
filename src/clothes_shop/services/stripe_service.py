import logging
import os
import string
from pathlib import Path
from typing import Any

import environ
import stripe
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))

logger = logging.getLogger(__name__)


class CheckoutData:
    def __init__(self, stripe_product_id: str, product_amount: int) -> None:
        self.stripe_product_id = stripe_product_id
        self.product_amount = product_amount


class StripeService:
    def __init__(self):
        stripe.api_key = env("STRIPE_SECRET_KEY")
        self.checkout_url_success = env("CHECKOUT_URL_SUCCESS")
        self.checkout_url_cancel = env("CHECKOUT_URL_CANCEL")

    def create_product(self, name: string, price: int) -> str:
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

    def checkout(
        self, checkout_data_list: list[CheckoutData]
    ) -> HttpResponseRedirect | HttpResponsePermanentRedirect:
        line_items: list[Any] = []
        for checkout_data in checkout_data_list:
            price_id: str = self.__get_price(checkout_data.stripe_product_id)
            line_items.append({"price": price_id, "quantity": checkout_data.product_amount})
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=self.checkout_url_success,
            cancel_url=self.checkout_url_cancel,
        )
        return redirect(session.url, code=303)
