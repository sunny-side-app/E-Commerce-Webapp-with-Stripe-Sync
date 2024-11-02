import random
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from clothes_shop.models import (
    Brand,
    CartItem,
    ClothesType,
    Product,
    Size,
    Target,
    User,
)


class Command(BaseCommand):
    help = "Seeds the database with product data using only Faker"

    def handle(self, *args, **kwargs):
        fake = Faker("ja_JP")

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

        product_data_count = 1000
        for _ in range(product_data_count):
            Product.objects.get_or_create(
                size=random.choice(size_list),
                target=random.choice(target_list),
                clothes_type=random.choice(clothes_type_list),
                brand=random.choice(brand_list),
                name=fake.text(max_nb_chars=40),
                description=fake.sentence(),
                category=random.choice(category_list),
                price=random.randint(1, 10000),
                release_date=timezone.make_aware(datetime.strptime("2018-12-05", "%Y-%m-%d")),
                stock_quantity=random.randint(0, 100),
            )
        user_data_count = 100
        for i in range(user_data_count):
            role_val = "registered"
            if i == 1 or i == 2:
                role_val = "admin"

            user, created = User.objects.get_or_create(
                name=fake.name(),
                defaults={  # 重複がない場合のみこれを使って新規作成
                    'email': fake.email(),
                    'role': role_val,
                    'email_validated_at': timezone.now(),
                    'address': fake.address(),
                }
            )

            if created:
                user.set_password("password")  # 任意のデフォルトパスワードを設定
                user.save()

        user_list = User.objects.all()
        product_list = Product.objects.all()

        for user in user_list:
            cartItems_num = random.randint(1, 10)
            for _ in range(cartItems_num):
                CartItem.objects.get_or_create(
                    user=user, product=random.choice(product_list), quantity=random.randint(1, 5)
                )

        print("Successfully seeded the database using Faker")
