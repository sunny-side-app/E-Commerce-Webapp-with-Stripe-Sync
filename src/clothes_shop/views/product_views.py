import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models.product import Product
from clothes_shop.models.user_interaction import Favorite
from clothes_shop.serializers.product_serializers import ProductSerializer
from clothes_shop.services.aws_service import AWS_Service
from clothes_shop.services.stripe_service import StripeService

logger = logging.getLogger(__name__)
stripe_service = StripeService()
aws_service = AWS_Service()


def get_product(product_id):
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


class ProductListView(APIView):

    def get_permissions(self):
        if self.request.method in ["POST", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()

    def get(self, request):
        size_ids = request.query_params.getlist("size[]")
        target_ids = request.query_params.getlist("target[]")
        clothes_type_ids = request.query_params.getlist("clothes_type[]")
        brand_ids = request.query_params.getlist("brand[]")
        keyword = request.query_params.get("keyword")
        is_deleted_param = request.query_params.get("is_deleted")
        release_date_param = request.query_params.get("release_date")

        filters = {}
        if size_ids:
            filters["size_id__in"] = size_ids
        if target_ids:
            filters["target_id__in"] = target_ids
        if clothes_type_ids:
            filters["clothes_type_id__in"] = clothes_type_ids
        if brand_ids:
            filters["brand_id__in"] = brand_ids

        if is_deleted_param is None:
            filters["is_deleted"] = False
        else:
            filters["is_deleted"] = is_deleted_param.lower() == "true"

        if release_date_param is None:
            filters["release_date__lt"] = timezone.now()
        else:
            try:
                release_date = timezone.datetime.fromisoformat(release_date_param)
                filters["release_date__lt"] = release_date
            except ValueError:
                errMsg = (
                    "フォーマットエラー。ISO format (e.g., 2023-09-30T10:00:00)を使用してください。"
                )
                logger.error(errMsg)
                return Response(
                    {"message": errMsg},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        products = Product.objects.filter(**filters).order_by("-release_date")
        if keyword:
            products = products.filter(name__icontains=keyword) | products.filter(
                description__icontains=keyword
            )

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_products = paginator.paginate_queryset(products, request)

        serializer_data = ProductSerializer(paginated_products, many=True).data
        # 認証ユーザーの場合は、各商品に対して`fav`をチェック]
        if request.user.is_authenticated:
            # ユーザーのお気に入り情報を取得
            user_favorite_product_ids = set(
                Favorite.objects.filter(user=request.user.id).values_list("product_id", flat=True)
            )
            logger.error(user_favorite_product_ids)
            for product in serializer_data:
                product["fav"] = product["id"] in user_favorite_product_ids
        else:
            # ゲストユーザーの場合はすべて`fav`を`False`に設定
            for product in serializer_data:
                product["fav"] = False
        return paginator.get_paginated_response(serializer_data)

    def post(self, request):
        product_img_file = request.FILES.get("imgFile")
        data = request.data.copy()
        data["img_url"] = None
        logger.error(data)

        if product_img_file:
            try:
                img_url = aws_service.upload_to_s3(product_img_file)
                data["img_url"] = img_url
                logger.error(img_url)
            except Exception as e:
                logger.error(f"画像のアップロード中にエラーが発生しました: {e}")
                return Response(
                    {"error": "画像のアップロードに失敗しました"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        serializer = ProductSerializer(data=data)

        if serializer.is_valid() is False:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        stripe_product_id = stripe_service.create_product(data["name"], data["price"])
        try:
            serializer.save(stripe_product_id=stripe_product_id)
        except Exception as e:
            logger.error(e)
            stripe_service.delete_product(stripe_product_id)
            raise e

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        product_ids = request.data["product_ids"]
        Product.objects.filter(id__in=product_ids).update(is_deleted=True)
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            stripe_service.delete_product(product.stripe_product_id)
        return Response(status=status.HTTP_200_OK)


class ProductDetailView(APIView):

    def get_permissions(self):
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        product = get_product(kwargs.get("pk"))
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        product = get_product(kwargs.get("pk"))
        product_img_file = request.FILES.get("imgFile")
        data = request.data.copy()
        data["img_url"] = None
        logger.error(data)
        if product_img_file:
            try:
                img_url = aws_service.upload_to_s3(product_img_file)
                data["img_url"] = img_url
                logger.error(img_url)

            except Exception as e:
                logger.error(f"画像のアップロード中にエラーが発生しました: {e}")
                return Response(
                    {"error": "画像のアップロードに失敗しました"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        serializer = ProductSerializer(product, data, partial=True)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        stripe_service.update_product(
            product.stripe_product_id,
            serializer.validated_data["name"],
            serializer.validated_data["price"],
        )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        product = get_product(kwargs.get("pk"))
        stripe_service.delete_product(product.stripe_product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
