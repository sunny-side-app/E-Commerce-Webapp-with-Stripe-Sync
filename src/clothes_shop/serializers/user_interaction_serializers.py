from rest_framework import serializers

from clothes_shop.models.user_interaction import Favorite, Review, WishList


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
    class Meta:
        model = Favorite
        fields = ("user", "product")


class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ("user", "product", "is_public")
