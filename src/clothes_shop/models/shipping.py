from django.db import models

from clothes_shop.models.order import Order


class Shipping(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipping_tracking_number = models.CharField(max_length=100)
    shipping_date = models.DateTimeField()
    shipping_address = models.CharField(max_length=255)
    address_code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
