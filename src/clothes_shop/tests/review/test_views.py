import logging
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.models.product import Product
from clothes_shop.models.user import User
from clothes_shop.models.user_interaction import Review
from clothes_shop.serializers.user_interaction_serializers import ReviewSerializer

logger = logging.getLogger(__name__)


class ReviewTests(APITestCase):
    def setUp(self):
        self.size = Size.objects.create(name="XL")
        self.target = Target.objects.create(name="メンズ")
        self.cloth_type = ClothesType.objects.create(name="シャツ")
        self.brand = Brand.objects.create(name="NIKE")
        self.one_week_ago = timezone.now() - timedelta(weeks=1)
        self.one_week_after = timezone.now() + timedelta(weeks=1)
        self.product_1 = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ１",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_1",
        )
        self.product_2 = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ２",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_2",
        )
        self.user_1 = User.objects.create(
            stripe_customer_id="user_1",
            name="たろう",
            email="test@hoge.commm",
            role="1",
            email_validated_at=self.one_week_ago,
            address="Japan",
        )
        self.user_2 = User.objects.create(
            stripe_customer_id="user_2",
            name="じろう",
            email="test@huga.commm",
            role="1",
            email_validated_at=self.one_week_ago,
            address="USA",
        )
        self.review_1_1 = Review.objects.create(
            user=self.user_1,
            product=self.product_1,
            rating=1,
            comment="たろう,テスト用につくったシャツ１",
        )
        self.review_1_2 = Review.objects.create(
            user=self.user_1,
            product=self.product_2,
            rating=2,
            comment="たろう,テスト用につくったシャツ２",
        )
        self.review_2_1 = Review.objects.create(
            user=self.user_2,
            product=self.product_1,
            rating=3,
            comment="じろう,テスト用につくったシャツ１",
        )
        self.review_2_2 = Review.objects.create(
            user=self.user_2,
            product=self.product_2,
            rating=5,
            comment="じろう,テスト用につくったシャツ２",
        )

    def test_product_review_list(self):
        product_review_list_url = reverse("clothes_shop:product-review-list")
        response = self.client.get(
            f"{product_review_list_url}?product_Id={self.product_1.id}&page=1"
        )

        review = Review.objects.filter(product_id=self.product_1.id)
        serializer = ReviewSerializer(review, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_user_review_list(self):
        user_review_list_url = reverse(
            "clothes_shop:user-review-list", kwargs={"user_id": self.user_1.id}
        )
        response = self.client.get(f"{user_review_list_url}?page=1")
        review = Review.objects.filter(user_id=self.user_1.id)
        serializer = ReviewSerializer(review, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_get_detail_review(self):
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": self.product_2.id, "user_id": self.user_2.id},
        )
        response = self.client.get(detail_url)
        review = Review.objects.filter(user_id=self.user_2.id, product_id=self.product_2.id).first()
        serializer = ReviewSerializer(review)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_detail_review_error_not_exist_product(self):
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": 0, "user_id": self.user_2.id},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_detail_review_error_not_exist_user(self):
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": self.product_2.id, "user_id": 0},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_detail_review(self):
        product_3 = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ３",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
        )
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": product_3.id, "user_id": self.user_1.id},
        )
        data = {"rating": 5, "comment": "たろう,テスト用につくったシャツ３"}
        response = self.client.post(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user_1.id)
        self.assertEqual(response.data["product"], product_3.id)
        self.assertEqual(response.data["rating"], data["rating"])
        self.assertEqual(response.data["comment"], data["comment"])

    def test_post_detail_review_error_invalid_rating(self):
        product_3 = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ３",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
        )
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": product_3.id, "user_id": self.user_1.id},
        )
        data = {"rating": 6, "comment": "たろう,テスト用につくったシャツ３"}
        response = self.client.post(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = {"rating": 0, "comment": "たろう,テスト用につくったシャツ３"}
        response = self.client.post(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_detail_review(self):
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": self.product_1.id, "user_id": self.user_1.id},
        )
        data = {"rating": 5, "comment": "たろう,テスト用につくったシャツ１ UPDATED"}
        response = self.client.put(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"], self.user_1.id)
        self.assertEqual(response.data["product"], self.product_1.id)
        self.assertEqual(response.data["rating"], data["rating"])
        self.assertEqual(response.data["comment"], data["comment"])

    def test_put_detail_review_error_not_exist_review(self):
        product_3 = Product.objects.create(
            size=self.size,
            target=self.target,
            clothes_type=self.cloth_type,
            brand=self.brand,
            name="テスト用につくったシャツ３",
            description="てすと",
            category="服",
            price=100,
            release_date=self.one_week_after,
            stock_quantity=500,
            is_deleted=False,
            stripe_product_id="product_3",
        )
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": product_3.id, "user_id": self.user_1.id},
        )
        data = {"rating": 5, "comment": "たろう,テスト用につくったシャツ１ UPDATED"}
        response = self.client.put(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_detail_review_error_invalid_rating(self):
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": self.product_1.id, "user_id": self.user_1.id},
        )
        data = {"rating": 0, "comment": "たろう,テスト用につくったシャツ１ UPDATED"}
        response = self.client.put(detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        detail_url = reverse(
            "clothes_shop:user-product-review-detail",
            kwargs={"product_id": self.product_1.id, "user_id": self.user_1.id},
        )
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
