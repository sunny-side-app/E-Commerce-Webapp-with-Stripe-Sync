import logging
import os
import random
from datetime import datetime
from pathlib import Path

import environ
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.models.cart import CartItem
from clothes_shop.models.order import Order, OrderItem
from clothes_shop.models.product import Product
from clothes_shop.models.user import User
from clothes_shop.models.user_interaction import Favorite, WishList
from clothes_shop.services.stripe_service import CustomerData, StripeService

BASE_DIR = Path(__file__).resolve().parents[4]
env = environ.Env()
env.read_env(os.path.join(os.path.dirname(BASE_DIR), ".env"))
demo_product_count = int(env("DEMO_PRODUCT_COUNT"))
demo_user_count = int(env("DEMO_USER_COUNT"))

fake = Faker("ja_JP")
logger = logging.getLogger(__name__)
stripe_service = StripeService()


class Command(BaseCommand):
    help = "Seeds the database with product data using only Faker"

    def handle(self, *args, **kwargs):
        size_name_list = ["S", "M", "L", "XL", "XXL"]
        target_name_list = ["メンズ", "レディース", "キッズ"]
        cloth_type_name_list = ["シャツ", "ズボン", "ジャケット", "アウター"]
        brand_name_list = ["CHANEL", "NIKE", "UNIQLO", "GU", "SHEIN"]
        category_list = ["服", "カタログ"]

        for name in size_name_list:
            Size.objects.get_or_create(name=name)

        for name in target_name_list:
            Target.objects.get_or_create(name=name)

        for name in cloth_type_name_list:
            ClothesType.objects.get_or_create(name=name)

        for name in brand_name_list:
            Brand.objects.get_or_create(name=name)

        size_list = Size.objects.all()
        target_list = Target.objects.all()
        clothes_type_list = ClothesType.objects.all()
        brand_list = Brand.objects.all()

        for _ in range(demo_product_count):
            name = fake.text(max_nb_chars=40)
            price = random.randint(1, 10000)
            stripe_product_id = stripe_service.create_product(name, price)
            Product.objects.get_or_create(
                size=random.choice(size_list),
                target=random.choice(target_list),
                clothes_type=random.choice(clothes_type_list),
                brand=random.choice(brand_list),
                name=name,
                description=fake.sentence(),
                category=random.choice(category_list),
                price=price,
                release_date=timezone.make_aware(datetime.strptime("2018-12-05", "%Y-%m-%d")),
                stock_quantity=random.randint(0, 100),
                stripe_product_id=stripe_product_id,
            )

        for i in range(demo_user_count):
            role_val = "admin" if i in (1, 2) else "registered"
            name = fake.name()
            email = fake.email()
            user, created = User.objects.get_or_create(
                name=name,
                defaults={  # 重複がない場合のみこれを使って新規作成
                    "stripe_customer_id": stripe_service.create_customer(CustomerData(name, email)),
                    "email": email,
                    "role": role_val,
                    "email_validated_at": timezone.now(),
                    "date_joined": timezone.now(),
                    "address": fake.address(),
                    "is_active": True,
                    "is_staff": True if role_val == "admin" else False,
                },
            )
            if created:
                user.set_password("password")  # 任意のデフォルトパスワードを設定
                user.save()

        user_list = User.objects.all()
        product_list = Product.objects.all()

        for user in user_list:
            cartItems_num = random.randint(1, 10)
            orders_num = random.randint(1, 3)
            fav_num = random.randint(1, 5)
            wish_num = random.randint(1, 5)

            cart_product_set = set()
            for _ in range(cartItems_num):
                product = random.choice(product_list)

                while (user.id, product.id) in cart_product_set:
                    product = random.choice(product_list)

                CartItem.objects.get_or_create(
                    user=user, product=product, defaults={"quantity": random.randint(1, 5)}
                )
                cart_product_set.add((user.id, product.id))

            favorite_product_set = set()
            for _ in range(fav_num):
                product = random.choice(product_list)

                while (user.id, product.id) in favorite_product_set:
                    product = random.choice(product_list)

                Favorite.objects.get_or_create(user=user, product=product)
                favorite_product_set.add((user.id, product.id))

            wish_product_set = set()
            for _ in range(wish_num):
                product = random.choice(product_list)

                while (user.id, product.id) in wish_product_set:
                    product = random.choice(product_list)

                WishList.objects.get_or_create(user=user, product=product)
                wish_product_set.add((user.id, product.id))

            for _ in range(orders_num):
                status_choices = [
                    "pending",
                    "confirmed",
                    "shipped",
                    "delivered",
                    "cancelled",
                    "returned",
                    "failed",
                    "completed",
                ]

                order = Order.objects.create(
                    user=user,
                    order_status=random.choice(status_choices),
                    total_price=0,
                    order_date=timezone.now(),
                )

                items_count = random.randint(1, 5)
                total_price = 0

                order_item_set = set()
                for _ in range(items_count):
                    product = random.choice(product_list)

                    while (order.id, product.id) in order_item_set:
                        product = random.choice(product_list)

                    quantity = random.randint(1, 3)
                    unit_price = product.price
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                    )

                    total_price += quantity * unit_price
                    order_item_set.add((order.id, product.id))

                order.total_price = total_price
                order.save()

        print("Successfully seeded the database using Faker")
