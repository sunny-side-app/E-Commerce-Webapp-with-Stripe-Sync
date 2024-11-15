import logging
from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.models.product import Product
from clothes_shop.models.user import User
from clothes_shop.models.user_interaction import Review
from clothes_shop.serializers.user_interaction_serializers import ReviewSerializer

logger = logging.getLogger(__name__)


class ProductReviewListViewTest(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")
        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")

        self.product_review = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ",
            description="てすと",
            category="服",
            price=100,
            release_date=timezone.make_aware(datetime.strptime("2018-12-05", "%Y-%m-%d")),
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_cart",
        )
        self.user = User.objects.create(
            name=fake.name(),
            email=fake.email(),
            role="registered",
            email_validated_at=timezone.now(),
            address=fake.address(),
            date_joined=timezone.now(),
            is_active=True,
            is_staff=True,
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.review = Review.objects.create(
            user=self.user, product=self.product_review, rating=4, comment="すごーい!"
        )

        self.list_url = reverse("clothes_shop:product-review-list")

    def test_get_reviews_with_product_id(self):
        response = self.client.get(f"{self.list_url}?product_Id={self.product_review.id}")
        reviews = Review.objects.filter(product_id=self.product_review.id).order_by("-created_at")

        serializer = ReviewSerializer(reviews, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("average_rating", response.data)
        self.assertEqual(response.data["average_rating"], 4)
        self.assertIn("is_ordered", response.data)
        self.assertEqual(response.data["results"], serializer.data)


class UserProductReviewDetailViewTest(APITestCase):
    def setUp(self):
        fake = Faker("ja_JP")
        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")

        self.product_new = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="カートに入っていない商品",
            description="てすと",
            category="服",
            price=100,
            release_date=timezone.make_aware(datetime.strptime("2018-12-05", "%Y-%m-%d")),
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_new",
        )

        self.user = User.objects.create(
            name=fake.name(),
            email=fake.email(),
            role="registered",
            email_validated_at=timezone.now(),
            address=fake.address(),
            date_joined=timezone.now(),
            is_active=True,
            is_staff=True,
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        self.review = Review.objects.create(
            user=self.user, product=self.product_new, rating=4, comment="すごーい!"
        )
        self.detail_url = reverse(
            "clothes_shop:user-product-review-detail", kwargs={"product_id": self.product_new.id}
        )

    def test_get_user_review_for_product(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 4)

    def test_post_create_review_for_product(self):
        data = {"rating": 5, "comment": "すごーい!"}
        response = self.client.post(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 5)
        self.assertEqual(response.data["comment"], "すごーい!")

    def test_post_update_existing_review(self):
        data = {"rating": 3, "comment": "そこそこ"}
        response = self.client.post(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rating"], 3)
        self.assertEqual(response.data["comment"], "そこそこ")
