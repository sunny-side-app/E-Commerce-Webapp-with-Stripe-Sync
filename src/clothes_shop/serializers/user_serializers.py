from rest_framework import serializers

# serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from clothes_shop.models.user import User
from clothes_shop.models.user_interaction import Favorite
from clothes_shop.serializers.user_interaction_serializers import FavoriteSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        favorite = Favorite.objects.filter(user=self.user)
        favorite_data = FavoriteSerializer(favorite, many=True).data
        fav_ids = []
        for fav in favorite_data:
            fav_ids.append(fav["product"])
        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "name": self.user.name,
                    "email": self.user.email,
                    "role": self.user.role,
                },
                "fav": fav_ids,
            }
        )

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "password",
            "role",
            "is_active",
            "is_staff",
            "address",
            "date_joined",
            "last_login",
            "created_at",
            "updated_at",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            name=validated_data["name"],
            role=validated_data["role"],
            address=validated_data.get("address", ""),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.name = validated_data.get("name", instance.name)
        instance.address = validated_data.get("address", instance.address)
        instance.role = validated_data.get("role", instance.role)
        if "password" in validated_data:
            instance.set_password(validated_data["password"])
        instance.save()
        return instance
