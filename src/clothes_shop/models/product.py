from django.db import models

from clothes_shop.models.attributes import Brand, ClothesType, Size, Target


class Product(models.Model):
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    clothes_type = models.ForeignKey(ClothesType, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    stripe_product_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=100)
    price = models.IntegerField()
    release_date = models.DateTimeField()
    stock_quantity = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
