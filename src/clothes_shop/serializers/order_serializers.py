from rest_framework import serializers

from clothes_shop.models.order import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("order", "product", "quantity", "unit_price")


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.StringRelatedField(many=True)

    class Meta:
        model = Order
        fields = ("id", "user", "order_date", "order_status", "total_price", "order_items")


class OrderListSerializer(serializers.ListSerializer):
    child = OrderSerializer()

    def create(self, validated_data):
        return [Order(**item) for item in validated_data]
