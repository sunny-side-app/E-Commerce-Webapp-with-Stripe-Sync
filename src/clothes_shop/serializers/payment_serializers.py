from rest_framework import serializers

from clothes_shop.models.payment import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("order", "payment_date", "payment_option", "payment_status")
