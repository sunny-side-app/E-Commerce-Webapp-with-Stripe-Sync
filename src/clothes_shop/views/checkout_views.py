import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from clothes_shop.permissions import IsCustomer, IsGuest
from clothes_shop.serializers.checkout_serializers import (
    CheckoutListSerializer,
    CheckoutSerializer,
)
from clothes_shop.services.stripe_service import CheckoutData, StripeService
from clothes_shop.views.product_views import get_product

logger = logging.getLogger(__name__)
striep_service = StripeService()


class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated & (IsCustomer | IsGuest)]

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
        role = request.user.role
        stripe_customer_id = request.user.stripe_customer_id
        redirect_url = striep_service.checkout(
            stripe_customer_id=stripe_customer_id if role != "guest" else None,
            checkout_data_list=checkout_data_list,
        )
        data = {"url": redirect_url}
        return Response(data, status=status.HTTP_200_OK)
