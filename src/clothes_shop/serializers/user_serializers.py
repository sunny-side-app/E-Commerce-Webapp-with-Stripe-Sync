from rest_framework import serializers

from clothes_shop.models.user import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "user_name", "email_address", "role", "address")
