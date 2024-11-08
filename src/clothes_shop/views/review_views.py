import logging

from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models.product import Product
from clothes_shop.models.user import User
from clothes_shop.models.user_interaction import Review
from clothes_shop.serializers.user_interaction_serializers import ReviewSerializer

logger = logging.getLogger(__name__)


class ProductReviewListView(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get("product_Id")
        if not product_id:
            return Response({"error": "product_Id is required"}, status=status.HTTP_400_BAD_REQUEST)

        reviews = Review.objects.filter(product_id=product_id)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserProductReviewDetailView(APIView):
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

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            errMsg = f"指定されたID {user_id} に紐づくユーザーが存在しません。"
            logger.error(errMsg)
            raise NotFound(detail=errMsg)
        except Exception as e:
            errMsg = f"想定外のエラーが発生しました: {str(e)}"
            logger.error(errMsg)
            raise APIException(detail=errMsg)

    def get(self, request, *args, **kwargs):
        product = self.get_product(kwargs["product_id"])
        user = self.get_user(kwargs["user_id"])
        review = Review.objects.filter(user_id=user.id, product_id=product.id).first()
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        product = self.get_product(kwargs["product_id"])
        user = self.get_user(kwargs["user_id"])
        data = {
            "user": user.id,
            "product": product.id,
            "rating": request.data["rating"],
            "comment": request.data["comment"],
        }
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid() is False:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        product = self.get_product(kwargs["product_id"])
        user = self.get_user(kwargs["user_id"])
        review = Review.objects.filter(user_id=user.id, product_id=product.id).first()
        if review is None:
            errMsg = (
                f"指定されたレビュー(user_id:{user.id},product_id:{product.id})は存在しません。"
            )
            logger.error(errMsg)
            return Response(errMsg, status=status.HTTP_400_BAD_REQUEST)
        data = {
            "rating": request.data["rating"],
            "comment": request.data["comment"],
        }
        serializer = ReviewSerializer(review, data=data, partial=True)
        if serializer.is_valid() is False:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        product = self.get_product(kwargs["product_id"])
        user = self.get_user(kwargs["user_id"])
        review = Review.objects.filter(user_id=user.id, product_id=product.id).first()
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserReviewListView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs["user_id"]
        reviews = Review.objects.filter(user_id=user_id)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)
