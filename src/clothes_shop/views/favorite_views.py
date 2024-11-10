import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models.product import Product
from clothes_shop.models.user import User
from clothes_shop.models.user_interaction import Favorite
from clothes_shop.serializers.user_interaction_serializers import FavoriteSerializer

logger = logging.getLogger(__name__)


class FavoriteListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        filters = {}
        filters["user_id"] = user_id
        favs = Favorite.objects.filter(**filters).order_by("-created_at")

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_products = paginator.paginate_queryset(favs, request)

        serializer_data = FavoriteSerializer(paginated_products, many=True).data

        return paginator.get_paginated_response(serializer_data)

    def post(self, request):
        user_id = request.user.id
        product_id = request.data.get("product_id")
        fav = request.data.get("fav")

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

        if fav == True:
            Favorite.objects.get_or_create(
                user_id=user_id,
                product_id=product_id,
            )
            return Response(
                {"message": f"product_id:{product_id}をFavoriteに追加しました。", "fav": True},
                status=status.HTTP_200_OK,
            )

        else:
            Favorite.objects.filter(user_id=user_id, product_id=product_id).delete()
            return Response(
                {"message": f"product_id:{product_id}をFavoriteから削除しました。", "fav": False},
                status=status.HTTP_200_OK,
            )


class FavoriteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer

    def get_object(self):
        return get_object_or_404(Favorite, pk=self.kwargs.get("pk"))
