import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models import CartItem, Product, User
from clothes_shop.serializers.cart_serializers import CartItemSerializer

logger = logging.getLogger(__name__)


class CartItemListCreateView(APIView):
    def get(self, request):
        # TODO　ログインユーザーで取得するようにする
        userId = request.query_params.get("user")
        filters = {}
        if userId:
            filters["user_id"] = userId
        else:
            errMsg = "userIdを設定してください。"
            logger.error(errMsg)
            raise NotFound(detail=errMsg)
        cartItems = CartItem.objects.filter(**filters).order_by("-created_at")
        serializer = CartItemSerializer(cartItems, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.data.get("user_id")
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")
        if not user_id or not product_id:
            errMsg = "userId、product_idを設定してください。"
            logger.error(errMsg)
            return Response(
                {"message": errMsg},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            User.objects.get(pk=user_id)
            Product.objects.get(pk=product_id)
        except User.DoesNotExist:
            errMsg = f"指定のuser_id:{user_id}は存在しません。"
            logger.error(errMsg)
            return Response(
                {"message": errMsg},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Product.DoesNotExist:
            errMsg = f"指定のproduct_id:{product_id}は存在しません。"
            logger.error(errMsg)
            return Response(
                {"message": errMsg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity is None:
            cart_item, is_created = CartItem.objects.get_or_create(
                user_id=user_id,
                product_id=product_id,
                defaults={"quantity": 1},
            )
            if not is_created:
                cart_item.quantity += 1
                cart_item.save()
                message = f"指定のproduct_id:{product_id}の数量を1増加しました。"
            else:
                message = f"指定のproduct_id:{product_id}はカートに新規登録されました。"
        else:
            cart_item, is_created = CartItem.objects.update_or_create(
                user_id=user_id,
                product_id=product_id,
                defaults={"quantity": quantity},
            )
            if is_created:
                message = f"指定のproduct_id:{product_id}はカートに新規登録されました。"
            else:
                message = f"指定のproduct_id:{product_id}の数量を変更しました。"
        return Response(
            {"message": message, "cart_item": CartItemSerializer(cart_item).data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        user_id = request.data.get("user_id")
        product_id = request.data.get("product_id")

        if not user_id or not product_id:
            errMsg = "userId、product_idを設定してください。"
            logger.error(errMsg)
            return Response(
                {"message": errMsg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            User.objects.get(pk=user_id)
            Product.objects.get(pk=product_id)
            CartItem.objects.get(
                user_id=user_id,
                product_id=product_id,
            )
        except User.DoesNotExist:
            errMsg = f"指定のuser_id:{user_id}は存在しません。"
            logger.error(errMsg)
            return Response(
                {"message": errMsg, "result": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Product.DoesNotExist:
            errMsg = f"指定のproduct_id:{product_id}は存在しません。"
            logger.error(errMsg)
            return Response(
                {"message": errMsg, "result": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        CartItem.objects.filter(user_id=user_id, product_id=product_id).delete()
        return Response(
            {"message": f"product_id:{product_id}をカートから削除しました。", "result": True},
            status=status.HTTP_200_OK,
        )


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_object(self):
        return get_object_or_404(CartItem, pk=self.kwargs.get("pk"))
