from rest_framework import serializers

from clothes_shop.models.user import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "stripe_customer_id",
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
            stripe_customer_id=validated_data["stripe_customer_id"],
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

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'password',
            'role', 
            'is_active', 
            'is_staff', 
            'address',
            ]
        read_only_fields = ['id', 'is_active', 'is_staff']
