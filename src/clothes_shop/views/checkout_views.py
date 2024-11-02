import logging

from rest_framework import status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.models import Product
from clothes_shop.serializers import CheckoutListSerializer, CheckoutSerializer
from clothes_shop.services.stripe_service import CheckoutData, StripeService

logger = logging.getLogger(__name__)
striep_service = StripeService()


def get_product(product_id) -> Product:
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


class StripeCheckoutView(APIView):
    def post(self, request):
        serializer = CheckoutListSerializer(data=request.data)
        if serializer.is_valid() is False:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        validated_data = serializer.validated_data
        checkout_instances = [
            CheckoutSerializer(data=checkout_data) for checkout_data in validated_data
        ]
        checkout_data_list: list[CheckoutData] = []
        for checkout_instance in checkout_instances:
            checkout_instance.is_valid()
            product_id = checkout_instance.validated_data["product_id"]
            amount = checkout_instance.validated_data["amount"]
            product = get_product(product_id)
            stripe_product_id = product.stripe_product_id
            checkout_data_list.append(CheckoutData(stripe_product_id, amount))
        return striep_service.checkout(checkout_data_list)
