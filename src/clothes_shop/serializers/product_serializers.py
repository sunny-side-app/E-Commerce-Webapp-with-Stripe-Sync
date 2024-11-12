from rest_framework import serializers

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target
from clothes_shop.models.product import Product
from clothes_shop.serializers.attributes_serializers import (
    BrandSerializer,
    ClothesTypeSerializer,
    SizeSerializer,
    TargetSerializer,
)


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
            "stripe_product_id",
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
            "img_url",
        )
        read_only_fields = (
            "id",
            "stripe_product_id",
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
