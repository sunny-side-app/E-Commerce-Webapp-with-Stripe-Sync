import logging

from django.db.models import Avg
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models.order import OrderItem
from clothes_shop.models.product import Product
from clothes_shop.models.user_interaction import Review
from clothes_shop.serializers.user_interaction_serializers import ReviewSerializer

logger = logging.getLogger(__name__)


class ProductReviewListView(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get("product_Id")
        if not product_id:
            return Response({"error": "product_Id is required"}, status=status.HTTP_400_BAD_REQUEST)

        reviews = Review.objects.filter(product_id=product_id).order_by("-created_at")
        average_rating = reviews.aggregate(Avg("rating"))["rating__avg"]
        is_ordered = False
        if request.user.is_authenticated:
            # 以前に購入したことがあるかを判断する
            product = Product.objects.get(pk=product_id)
            previous_order = OrderItem.objects.filter(
                order__user=request.user, product=product
            ).exists()
            if previous_order:
                is_ordered = True
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginated_reviews, many=True)

        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data["average_rating"] = average_rating
        paginated_response.data["is_ordered"] = is_ordered

        return paginated_response


class UserProductReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_product(self, product_id):
        try:
            product = Product.objects.get(pk=product_id)
            return product
        except Product.DoesNotExist:
            errMsg = f"指定されたID {product_id} に紐づく製品が存在しません。"
            logger.error(errMsg)
            raise NotFound(detail=errMsg)
        except Exception as e:
            errMsg = f"想定外のエラーが発生しました: {str(e)}"
            logger.error(errMsg)
            raise APIException(detail=errMsg)

    def get(self, request, *args, **kwargs):
        product = self.get_product(kwargs["product_id"])
        user = request.user
        review = Review.objects.filter(user_id=user.id, product_id=product).first()
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        product = self.get_product(kwargs["product_id"])
        user = request.user

        try:
            review = Review.objects.get(user=user, product=product)
            is_update = True
        except Review.DoesNotExist:
            review = None
            is_update = False
        data = {
            "user": user.id,
            "product": product.id,
            "rating": request.data["rating"],
            "comment": request.data["comment"],
        }

        if is_update:
            serializer = ReviewSerializer(review, data=data)
        else:
            serializer = ReviewSerializer(data=data)
        if serializer.is_valid() is False:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
