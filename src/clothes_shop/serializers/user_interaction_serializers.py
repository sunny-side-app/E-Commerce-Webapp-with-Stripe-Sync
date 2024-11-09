from rest_framework import serializers

from clothes_shop.models.product import Product
from clothes_shop.models.user_interaction import Favorite, Review, WishList
from clothes_shop.serializers.product_serializers import ProductSerializer


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "product",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        )


class FavoriteSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(read_only=True)
    product_pk = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = Favorite
        fields = ("user", "product", "product_pk")

    def get_product(self, obj: Favorite):
        return ProductSerializer(obj.product).data


class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ("user", "product", "is_public")
