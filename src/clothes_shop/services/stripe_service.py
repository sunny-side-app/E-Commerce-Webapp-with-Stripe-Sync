import os
import string
from pathlib import Path

import environ
import stripe

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))


class StripeService:
    def __init__(self):
        stripe.api_key = env("STRIPE_SECRET_KEY")

    def create_product(self, product_data: stripe.Product):
        return stripe.Product.create(**product_data)

    def update_product(self, product_data: stripe.Product):
        return stripe.Product.modify(**product_data)

    def retrieve_product(self, id: string):
        return stripe.Product.retrieve(id=id)

    def list_all_product(self):
        return stripe.Product.list(limit=10)

    def delete_product(self, id: string):
        return stripe.Product.delete(id=id)
