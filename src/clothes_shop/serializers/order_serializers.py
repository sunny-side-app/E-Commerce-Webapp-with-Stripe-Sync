from rest_framework import serializers

from clothes_shop.models.order import Order, OrderItem
from clothes_shop.models.product import Product
from clothes_shop.models.user import User
from clothes_shop.serializers.product_serializers import ProductSerializer
from clothes_shop.serializers.user_serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(read_only=True)
    product_pk = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = OrderItem
        fields = ("order", "product", "quantity", "unit_price", "product_pk")

    def get_product(self, obj: Order):
        return ProductSerializer(obj.product).data


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    user = serializers.SerializerMethodField(read_only=True)
    user_pk = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Order

        fields = (
            "id",
            "user",
            "order_date",
            "order_status",
            "total_price",
            "order_items",
            "user_pk",
        )

    def get_user(self, obj: Order):
        return UserSerializer(obj.user).data

    def create(self, validated_data):
        user = validated_data.pop("user_pk")
        order = Order.objects.create(user=user, **validated_data)
        return order


class OrderListSerializer(serializers.ListSerializer):
    child = OrderSerializer()

    def create(self, validated_data):
        return [Order(**item) for item in validated_data]
