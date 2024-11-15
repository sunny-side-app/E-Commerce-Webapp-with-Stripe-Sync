import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models.product import Product
from clothes_shop.models.user_interaction import WishList
from clothes_shop.serializers.user_interaction_serializers import WishListSerializer

logger = logging.getLogger(__name__)


class WishListListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        filters = {}
        filters["user_id"] = user_id
        wishs = WishList.objects.filter(**filters).order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_products = paginator.paginate_queryset(wishs, request)

        serializer_data = WishListSerializer(paginated_products, many=True).data

        return paginator.get_paginated_response(serializer_data)

    def post(self, request):
        user_id = request.user.id
        product_id = request.data.get("product_id")
        wish = request.data.get("wish")

        if not product_id:
            errMsg = "product_idを設定してください。"
            logger.error(errMsg)
            raise NotFound(detail=errMsg)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            errMsg = f"指定のproduct_id:{product_id}は存在しません。"
            logger.error(errMsg)
            raise NotFound(detail=errMsg)

        if wish == True:
            WishList.objects.get_or_create(
                user_id=user_id,
                product_id=product_id,
            )
            return Response(
                {"message": f"product_id:{product_id}をWishListに追加しました。", "wish": True},
                status=status.HTTP_200_OK,
            )

        else:
            WishList.objects.filter(user_id=user_id, product_id=product_id).delete()
            return Response(
                {"message": f"product_id:{product_id}をWishListから削除しました。", "wish": False},
                status=status.HTTP_200_OK,
            )


class WishListDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer

    def get_object(self):
        return get_object_or_404(WishList, pk=self.kwargs.get("pk"))
