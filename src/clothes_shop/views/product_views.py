import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models import Product
from clothes_shop.serializers import ProductSerializer

logger = logging.getLogger(__name__)


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

        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid() is False:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        product_ids = request.data["product_ids"]
        for product_id in product_ids:
            try:
                product = get_product(product_id)
                product.delete()
            except Exception:
                errMsg = f"指定されたID {product_id} の削除に失敗しました。"
                logger.error(errMsg)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductDetailView(APIView):
    def get(self, request, *args, **kwargs):
        product = get_product(kwargs.get("pk"))
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        product = get_product(kwargs.get("pk"))
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        product = get_product(kwargs.get("pk"))
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
