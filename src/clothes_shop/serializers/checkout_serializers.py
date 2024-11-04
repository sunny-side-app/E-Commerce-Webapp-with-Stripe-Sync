from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=255)
    amount = serializers.IntegerField()


class CheckoutListSerializer(serializers.ListSerializer):
    child = CheckoutSerializer()
    allow_empty = False
