from rest_framework import serializers

from clothes_shop.models.shipping import Shipping


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = (
            "order",
            "shipping_tracking_number",
            "shipping_date",
            "shipping_address",
            "address_code",
        )
