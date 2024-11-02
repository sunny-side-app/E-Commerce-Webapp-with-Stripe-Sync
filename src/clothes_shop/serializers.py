from rest_framework import serializers

from .models import (
    Brand,
    CartItem,
    ClothesType,
    Favorite,
    Order,
    OrderItem,
    Payment,
    Product,
    Review,
    Shipping,
    Size,
    Target,
    User,
    WishList,
)


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ClothesTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothesType
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ProductSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)
    clothes_type = serializers.SerializerMethodField(read_only=True)
    brand = serializers.SerializerMethodField(read_only=True)
    size_pk = serializers.PrimaryKeyRelatedField(queryset=Size.objects.all(), write_only=True)
    target_pk = serializers.PrimaryKeyRelatedField(queryset=Target.objects.all(), write_only=True)
    clothes_type_pk = serializers.PrimaryKeyRelatedField(
        queryset=ClothesType.objects.all(), write_only=True
    )
    brand_pk = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), write_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "price",
            "stock_quantity",
            "release_date",
            "size",
            "target",
            "clothes_type",
            "brand",
            "size_pk",
            "target_pk",
            "clothes_type_pk",
            "brand_pk",
            "category",
            "is_deleted",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )

    def get_size(self, obj: Product):
        return SizeSerializer(obj.size).data

    def get_target(self, obj: Product):
        return TargetSerializer(obj.target).data

    def get_clothes_type(self, obj: Product):
        return ClothesTypeSerializer(obj.clothes_type).data

    def get_brand(self, obj: Product):
        return BrandSerializer(obj.brand).data

    def create(self, validated_data: dict[str, any]) -> Product:
        pk_fields = ["size_pk", "target_pk", "clothes_type_pk", "brand_pk"]
        for pk_field in pk_fields:
            related_field = pk_field.replace("_pk", "")
            pk_value = validated_data.get(pk_field, None)
            if pk_value is not None:
                validated_data[related_field] = pk_value
                del validated_data[pk_field]
        return super().create(validated_data)

    def update(self, instance, validated_data: dict[str, any]) -> Product:
        pk_fields = ["size_pk", "target_pk", "clothes_type_pk", "brand_pk"]
        for pk_field in pk_fields:
            related_field = pk_field.replace("_pk", "")
            pk_value = validated_data.get(pk_field, None)
            if pk_value is not None:
                validated_data[related_field] = pk_value
                del validated_data[pk_field]
        return super().update(instance, validated_data)


# Order Serializer (for detail view)
class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.StringRelatedField(many=True)

    class Meta:
        model = Order
        fields = ("id", "user", "order_date", "order_status", "total_price", "order_items")


# Order List Serializer (for listing orders)
class OrderListSerializer(serializers.ListSerializer):
    child = OrderSerializer()

    def create(self, validated_data):
        return [Order(**item) for item in validated_data]


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


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'email', 
            'name', 
            'password', 
            'role', 
            'is_active', 
            'is_staff', 
            'address',
            'date_joined', 
            'last_login',
            'created_at', 
            'updated_at'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
            role=validated_data['role'],
            address=validated_data.get('address', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.address = validated_data.get('address', instance.address)
        instance.role = validated_data.get('role', instance.role)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance


# Favorite Serializer
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ("user", "product")


# WishList Serializer
class WishListSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishList
        fields = ("user", "product", "is_public")


# CartItem Serializer
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("user", "product", "quantity")


# OrderItem Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("order", "product", "quantity", "unit_price")


# Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("order", "payment_date", "payment_option", "payment_status")


# Shipping Serializer
class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        fields = (
            "order",
            "shipping_tracking_number",
            "shipping_date",
            "shipping_address",
            "address_code",
        )
