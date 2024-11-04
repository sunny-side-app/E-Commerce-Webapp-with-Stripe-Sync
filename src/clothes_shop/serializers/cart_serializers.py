from rest_framework import serializers

from clothes_shop.models.cart import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("user", "product", "quantity")
