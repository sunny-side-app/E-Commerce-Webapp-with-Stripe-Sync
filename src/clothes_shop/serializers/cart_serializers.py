from rest_framework import serializers

from clothes_shop.models.cart import CartItem, Product, User
from clothes_shop.serializers.product_serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    user_pk = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    product = serializers.SerializerMethodField(read_only=True)
    product_pk = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = CartItem

        fields = (
            "user",
            "product",
            "quantity",
            "user_pk",
            "product_pk",
        )

    def get_product(self, obj: CartItem):
        return ProductSerializer(obj.product).data

    def create(self, validated_data: dict[str, any]) -> CartItem:
        pk_fields = ["user_pk", "product_pk"]
        for pk_field in pk_fields:
            related_field = pk_field.replace("_pk", "")
            pk_value = validated_data.get(pk_field, None)
            if pk_value is not None:
                validated_data[related_field] = pk_value
                del validated_data[pk_field]
        return super().create(validated_data)

    def update(self, instance, validated_data: dict[str, any]) -> CartItem:
        pk_fields = ["product_pk"]
        for pk_field in pk_fields:
            related_field = pk_field.replace("_pk", "")
            pk_value = validated_data.get(pk_field, None)
            if pk_value is not None:
                validated_data[related_field] = pk_value
                del validated_data[pk_field]
        return super().update(instance, validated_data)
